from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('test-csrf/', views.test_csrf, name='test_csrf'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('register/', views.user_register, name='user_register'),
    path('contractor/register/', views.contractor_register, name='contractor_register'),
    
    # User URLs
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/complaint/new/', views.post_complaint, name='post_complaint'),
    path('user/complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('user/notifications/', views.user_notifications, name='user_notifications'),
    

    
    # Contractor URLs
    path('contractor/dashboard/', views.contractor_dashboard, name='contractor_dashboard'),
    path('contractor/assignment/<int:assignment_id>/update/', views.update_status, name='update_status'),
    path('contractor/notifications/', views.contractor_notifications, name='contractor_notifications'),
]