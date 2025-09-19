from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Contractor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    specialization = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.user.username}"

class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('pothole', 'Pothole'),
        ('construction', 'Construction'),
        ('maintenance', 'Maintenance'),
        ('traffic_signal', 'Traffic Signal'),
        ('street_light', 'Street Light'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('assigned', 'Assigned to Contractor'),
        ('in_progress', 'Work In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_TYPES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_complaints')
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

class ComplaintAssignment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    estimated_completion_date = models.DateField(null=True, blank=True)
    status_update = models.TextField(blank=True)
    work_started_at = models.DateTimeField(null=True, blank=True)
    work_completed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.complaint.title} - {self.contractor.company_name}"

class ComplaintUpdate(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    update_text = models.TextField()
    update_image = models.ImageField(upload_to='updates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for {self.complaint.title} by {self.contractor.company_name}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('complaint_status', 'Complaint Status Update'),
        ('assignment', 'New Assignment'),
        ('verification', 'Complaint Verified'),
        ('completion', 'Work Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}" 