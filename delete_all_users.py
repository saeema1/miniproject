#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RoadSafety.settings')
django.setup()

from django.contrib.auth.models import User
from roadapp.models import Complaint, Contractor, ComplaintAssignment, ComplaintUpdate, Notification

print("=== WARNING: This will delete ALL users and related data ===")
print("This includes:")
print("- All regular users")
print("- All admin users") 
print("- All contractors")
print("- All complaints")
print("- All assignments and updates")
print("- All notifications")
print()

# Count current data
print("=== Current Data Count ===")
print(f"Users: {User.objects.count()}")
print(f"Complaints: {Complaint.objects.count()}")
print(f"Contractors: {Contractor.objects.count()}")
print(f"Complaint Assignments: {ComplaintAssignment.objects.count()}")
print(f"Complaint Updates: {ComplaintUpdate.objects.count()}")
print(f"Notifications: {Notification.objects.count()}")
print()

# Show current users
print("=== Current Users ===")
for user in User.objects.all():
    staff_status = "ADMIN" if user.is_staff else "USER"
    print(f"{staff_status}: {user.username} ({user.email})")
print()

# Ask for confirmation
confirm = input("Are you sure you want to delete ALL users and data? Type 'YES' to confirm: ")

if confirm == "YES":
    print("\n=== Deleting all data... ===")
    
    # Delete in correct order to avoid foreign key constraint issues
    print("Deleting notifications...")
    Notification.objects.all().delete()
    
    print("Deleting complaint updates...")
    ComplaintUpdate.objects.all().delete()
    
    print("Deleting complaint assignments...")
    ComplaintAssignment.objects.all().delete()
    
    print("Deleting complaints...")
    Complaint.objects.all().delete()
    
    print("Deleting contractors...")
    Contractor.objects.all().delete()
    
    print("Deleting all users...")
    User.objects.all().delete()
    
    print("\n=== Deletion Complete ===")
    print("All users and related data have been removed.")
    print("You will need to create a new superuser to access the admin panel.")
    print("\nTo create a new superuser, run:")
    print("python manage.py createsuperuser")
    
else:
    print("\nDeletion cancelled. No data was removed.")
