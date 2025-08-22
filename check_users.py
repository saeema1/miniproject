import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RoadSafety.settings')
django.setup()

from django.contrib.auth.models import User

print("=== Database User Check ===")
print(f"Total users: {User.objects.count()}")

admin_users = User.objects.filter(is_staff=True)
print(f"Admin users: {admin_users.count()}")

if admin_users.exists():
    print("\nAdmin users found:")
    for user in admin_users:
        print(f"- Username: {user.username}, Email: {user.email}, Superuser: {user.is_superuser}")
else:
    print("\nNo admin users found!")
    print("You need to create an admin user.")

print("\n=== End Check ===") 