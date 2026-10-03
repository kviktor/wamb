from django import forms
from django.core.exceptions import ValidationError

from app.users.models import User


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email):
            raise ValidationError("A user with this email already exists")

        return email

    def clean(self):
        super().clean()

        email = self.cleaned_data.get("email")
        if email:
            self.cleaned_data["username"] = email

    def save(self, *args, **kwargs):
        return User.objects.create_user(**self.cleaned_data)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "can_view", "can_change", "can_manage_users")
