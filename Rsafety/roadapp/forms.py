from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Complaint, Contractor, ComplaintUpdate, ComplaintAssignment

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class ContractorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    company_name = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    specialization = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'location', 'complaint_type', 'priority', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'complaint_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ComplaintUpdateForm(forms.ModelForm):
    class Meta:
        model = ComplaintUpdate
        fields = ['update_text', 'update_image']
        widgets = {
            'update_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'update_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ComplaintAssignmentForm(forms.ModelForm):
    class Meta:
        model = ComplaintAssignment
        fields = ['contractor', 'estimated_completion_date', 'status_update']
        widgets = {
            'contractor': forms.Select(attrs={'class': 'form-control'}),
            'estimated_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status_update': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 