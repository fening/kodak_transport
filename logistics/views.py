from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer

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

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)

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


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TransportRecord
from .serializers import TransportRecordSerializer

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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransportRecordDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransportRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransportRecord.objects.filter(user=self.request.user)
    
    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import TransportRecord
from datetime import datetime, timedelta

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        records = TransportRecord.objects.filter(user=user)

        # Calculate summary statistics
        total_miles = records.aggregate(Sum('miles'))['miles__sum'] or 0
        total_pay = records.aggregate(Sum('pay'))['pay__sum'] or 0
        record_count = records.count()

        # Get recent records
        recent_records = records.order_by('-date')[:5].values('id', 'date', 'po_number', 'miles', 'pay')

        # Calculate monthly data
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