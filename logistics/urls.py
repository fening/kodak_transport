from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('records/', views.TransportRecordList.as_view(), name='record-list'),
    path('records/add/', views.AddTransportRecord.as_view(), name='add-record'),
    path('records/<int:pk>/', views.TransportRecordDetail.as_view(), name='record-detail'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]