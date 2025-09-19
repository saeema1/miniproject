from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('complaint/<int:complaint_id>/verify/', views.verify_complaint, name='verify_complaint'),
    path('complaint/<int:complaint_id>/assign/', views.assign_contractor, name='assign_contractor'),
    path('contractors/', views.view_contractors, name='view_contractors'),
    path('contractor/<int:contractor_id>/verify/', views.verify_contractor, name='verify_contractor'),
    path('search/email/', views.search_by_email, name='search_by_email'),
]
