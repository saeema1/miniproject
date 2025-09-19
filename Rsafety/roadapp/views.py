from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .models import Complaint, Contractor, ComplaintAssignment, ComplaintUpdate, Notification
from .forms import UserRegistrationForm, ContractorRegistrationForm, ComplaintForm, ComplaintUpdateForm, ComplaintAssignmentForm

def is_admin(user):
    return user.is_staff

def is_contractor(user):
    return hasattr(user, 'contractor')

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        # Debug: Print CSRF token info
        print(f"CSRF Token from form: {request.POST.get('csrfmiddlewaretoken', 'NOT_FOUND')}")
        print(f"CSRF Token from cookies: {request.COOKIES.get('csrftoken', 'NOT_FOUND')}")
        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            elif hasattr(user, 'contractor'):
                return redirect('contractor_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def test_csrf(request):
    """Test view to verify CSRF is working"""
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'CSRF token is working!'})
    return render(request, 'test_csrf.html')

def forgot_password(request):
    """Handle forgot password requests"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Request - Road Safety System"
                    email_template_name = "registration/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': get_current_site(request).domain,
                        'site_name': 'Road Safety System',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'noreply@roadsafety.com', [user.email], fail_silently=False)
                        messages.success(request, 'Password reset email has been sent to your email address.')
                    except Exception as e:
                        messages.error(request, 'Failed to send password reset email. Please try again.')
            else:
                messages.error(request, 'No user found with this email address.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/forgot_password.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    """Handle password reset confirmation"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('login')

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('user_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'user_registration.html', {'form': form})

def contractor_register(request):
    if request.method == 'POST':
        form = ContractorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            contractor = Contractor.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                specialization=form.cleaned_data['specialization']
            )
            login(request, user)
            messages.success(request, 'Contractor account created successfully!')
            return redirect('contractor_dashboard')
    else:
        form = ContractorRegistrationForm()
    return render(request, 'contractor_registration.html', {'form': form})

# User Views
@login_required
def user_dashboard(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'complaints': complaints,
        'total_complaints': complaints.count(),
        'pending_complaints': complaints.filter(status='pending').count(),
        'completed_complaints': complaints.filter(status='completed').count(),
    }
    return render(request, 'user/user_index.html', context)

@login_required
def post_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
            return redirect('user_dashboard')
    else:
        form = ComplaintForm()
    return render(request, 'user/cmplaintreg.html', {'form': form})

@login_required
def complaint_detail(request, complaint_id):
    # Allow admins to view any complaint; regular users can only view their own
    if request.user.is_staff:
        complaint = get_object_or_404(Complaint, id=complaint_id)
    else:
        complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    updates = ComplaintUpdate.objects.filter(complaint=complaint).order_by('-created_at')
    context = {
        'complaint': complaint,
        'updates': updates,
    }
    return render(request, 'user/complaint_detail.html', context)

@login_required
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/notifications.html', {'notifications': notifications})

# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    contractors = Contractor.objects.all()
    
    # Email search functionality
    search_email = request.GET.get('search_email', '')
    if search_email:
        # Search in users by email
        users_by_email = User.objects.filter(email__icontains=search_email)
        contractors_by_email = contractors.filter(user__email__icontains=search_email)
        complaints_by_email = complaints.filter(user__email__icontains=search_email)
    else:
        users_by_email = User.objects.none()
        contractors_by_email = contractors.none()
        complaints_by_email = complaints.none()
    
    context = {
        'complaints': complaints,
        'contractors': contractors,
        'total_complaints': complaints.count(),
        'pending_complaints': complaints.filter(status='pending').count(),
        'verified_complaints': complaints.filter(status='verified').count(),
        'assigned_complaints': complaints.filter(status='assigned').count(),
        'completed_complaints': complaints.filter(status='completed').count(),
        'verified_contractors': contractors.filter(is_verified=True).count(),
        # Email search results
        'search_email': search_email,
        'users_by_email': users_by_email,
        'contractors_by_email': contractors_by_email,
        'complaints_by_email': complaints_by_email,
    }
    return render(request, 'admin/admin_index.html', context)

@login_required
@user_passes_test(is_admin)
def verify_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            complaint.status = 'verified'
            complaint.verified_by = request.user
            complaint.verified_at = timezone.now()
            complaint.save()
            messages.success(request, 'Complaint verified successfully!')
        elif action == 'reject':
            complaint.status = 'rejected'
            complaint.save()
            messages.success(request, 'Complaint rejected!')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def assign_contractor(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = ComplaintAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.complaint = complaint
            assignment.assigned_by = request.user
            assignment.save()
            complaint.status = 'assigned'
            complaint.save()
            messages.success(request, 'Complaint assigned to contractor successfully!')
            return redirect('admin_dashboard')
    else:
        form = ComplaintAssignmentForm()
    
    context = {
        'complaint': complaint,
        'form': form,
        'contractors': Contractor.objects.filter(is_verified=True)
    }
    return render(request, 'admin/assign_contractor.html', context)

@login_required
@user_passes_test(is_admin)
def view_contractors(request):
    contractors = Contractor.objects.all().order_by('-created_at')
    return render(request, 'admin/contractors.html', {'contractors': contractors})

@login_required
@user_passes_test(is_admin)
def verify_contractor(request, contractor_id):
    contractor = get_object_or_404(Contractor, id=contractor_id)
    contractor.is_verified = True
    contractor.save()
    messages.success(request, f"Contractor '{contractor.company_name}' verified.")
    return redirect('view_contractors')

@login_required
@user_passes_test(is_admin)
def search_by_email(request):
    """Search users, contractors, and complaints by email"""
    search_email = request.GET.get('email', '')
    results = {}
    
    if search_email:
        # Search users by email
        users = User.objects.filter(email__icontains=search_email)
        results['users'] = users
        
        # Search contractors by email
        contractors = Contractor.objects.filter(user__email__icontains=search_email)
        results['contractors'] = contractors
        
        # Search complaints by user email
        complaints = Complaint.objects.filter(user__email__icontains=search_email)
        results['complaints'] = complaints
    else:
        # Initialize empty querysets when no search
        results['users'] = User.objects.none()
        results['contractors'] = Contractor.objects.none()
        results['complaints'] = Complaint.objects.none()
    
    context = {
        'search_email': search_email,
        'results': results,
        'has_results': bool(results.get('users') or results.get('contractors') or results.get('complaints'))
    }
    return render(request, 'admin/email_search.html', context)

# Contractor Views
@login_required
@user_passes_test(is_contractor)
def contractor_dashboard(request):
    assignments = ComplaintAssignment.objects.filter(
        contractor=request.user.contractor,
        is_active=True
    ).order_by('-assigned_at')
    
    context = {
        'assignments': assignments,
        'total_assignments': assignments.count(),
        'active_assignments': assignments.filter(complaint__status='assigned').count(),
        'in_progress_assignments': assignments.filter(complaint__status='in_progress').count(),
        'completed_assignments': assignments.filter(complaint__status='completed').count(),
    }
    return render(request, 'contractor/contractor_index.html', context)

@login_required
@user_passes_test(is_contractor)
def update_status(request, assignment_id):
    assignment = get_object_or_404(ComplaintAssignment, id=assignment_id, contractor=request.user.contractor)
    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, request.FILES)

        # Always try to update status, even if no text/image provided
        new_status = request.POST.get('status')
        if new_status:
            assignment.complaint.status = new_status
            assignment.complaint.save()

            if new_status == 'in_progress' and not assignment.work_started_at:
                assignment.work_started_at = timezone.now()
            elif new_status == 'completed' and not assignment.work_completed_at:
                assignment.work_completed_at = timezone.now()

            assignment.save()

        # Create a progress note only if provided/valid
        if form.is_valid() and (form.cleaned_data.get('update_text') or form.cleaned_data.get('update_image')):
            update = form.save(commit=False)
            update.complaint = assignment.complaint
            update.contractor = request.user.contractor
            update.save()

        if new_status:
            messages.success(request, 'Status updated successfully!')
            return redirect('contractor_dashboard')
        else:
            messages.error(request, 'Please select a status to update.')
    else:
        form = ComplaintUpdateForm()
    
    context = {
        'assignment': assignment,
        'form': form,
    }
    return render(request, 'contractor/update_status.html', context)

@login_required
@user_passes_test(is_contractor)
def contractor_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'contractor/notifications.html', {'notifications': notifications})

# General Views
def home(request):
    # Always show the home page, regardless of login status
    return render(request, 'index.html') 