from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import logging
from .serializers import UserSerializer, TransportRecordSerializer, NotificationSerializer
from .models import TransportRecord, Notification

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    logger.info(f"Received registration request with data: {request.data}")
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "User registered successfully",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_201_CREATED)
    logger.error(f"Registration failed. Errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransportRecordList(generics.ListAPIView):
    serializer_class = TransportRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransportRecord.objects.filter(user=self.request.user)

class AddTransportRecord(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TransportRecordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            record = serializer.save()
            create_notification(
                user=request.user,
                message=f"New record added: {record.po_number}",
                link=f"/records/{record.id}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransportRecordDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransportRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransportRecord.objects.filter(user=self.request.user)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        records = TransportRecord.objects.filter(user=user)

        total_miles = records.aggregate(Sum('miles'))['miles__sum'] or 0
        total_pay = records.aggregate(Sum('pay'))['pay__sum'] or 0
        record_count = records.count()

        recent_records = records.order_by('-date')[:5].values('id', 'date', 'po_number', 'miles', 'pay')

        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_data = records.filter(date__gte=six_months_ago) \
            .annotate(month=TruncMonth('date')) \
            .values('month') \
            .annotate(miles=Sum('miles'), pay=Sum('pay')) \
            .order_by('month')

        monthly_data = [
            {
                'month': item['month'].strftime('%B %Y'),
                'miles': item['miles'],
                'pay': item['pay']
            } for item in monthly_data
        ]

        return Response({
            'totalMiles': total_miles,
            'totalPay': total_pay,
            'recordCount': record_count,
            'recentRecords': recent_records,
            'monthlyData': monthly_data
        })

class NotificationList(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Check for a query parameter to filter read/unread notifications
        show_all = self.request.query_params.get('show_all', 'false').lower() == 'true'
        if show_all:
            return Notification.objects.filter(user=self.request.user)
        return Notification.objects.filter(user=self.request.user, is_read=False)

class MarkNotificationAsRead(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"status": "success"})
        except Notification.DoesNotExist:
            return Response({"status": "error", "message": "Notification not found"}, status=404)

def create_notification(user, message, link):
    Notification.objects.create(user=user, message=message, link=link)