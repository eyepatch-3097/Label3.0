from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    def confirm_login_allowed(self, user):
        # Block login if user is pending approval
        if hasattr(user, "status") and user.status == User.STATUS_PENDING:
            raise forms.ValidationError(
                "Your account is awaiting admin approval. Please try again later.",
                code='inactive',
            )


class SignupStep1Form(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned


class SignupOrgForm(forms.Form):
    org_name = forms.CharField(
        label="Organisation Name",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
