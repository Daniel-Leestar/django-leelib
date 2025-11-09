from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '旧密码'}),
        label='旧密码'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '新密码'}),
        label='新密码'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '确认新密码'}),
        label='确认新密码'
    )
