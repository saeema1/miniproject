from django.contrib import admin
from .models import Contractor, Complaint, ComplaintAssignment, ComplaintUpdate, Notification

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'phone', 'specialization', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'specialization', 'created_at']
    search_fields = ['company_name', 'user__username', 'phone']
    list_editable = ['is_verified']

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'complaint_type', 'priority', 'status', 'location', 'created_at']
    list_filter = ['status', 'complaint_type', 'priority', 'created_at']
    search_fields = ['title', 'description', 'location', 'user__username']
    list_editable = ['status', 'priority']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ComplaintAssignment)
class ComplaintAssignmentAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'contractor', 'assigned_by', 'assigned_at', 'is_active']
    list_filter = ['is_active', 'assigned_at']
    search_fields = ['complaint__title', 'contractor__company_name']
    readonly_fields = ['assigned_at']

@admin.register(ComplaintUpdate)
class ComplaintUpdateAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'contractor', 'created_at']
    list_filter = ['created_at']
    search_fields = ['complaint__title', 'contractor__company_name', 'update_text']
    readonly_fields = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at'] 