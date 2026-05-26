from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES
    )

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'password'
        ]