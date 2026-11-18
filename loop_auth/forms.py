import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150, label="Your name")
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    terms = forms.BooleanField()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Your password must include at least one number.")
        return password

    def save(self):
        name = self.cleaned_data["name"].strip()
        email = self.cleaned_data["email"]
        base = email.split("@")[0][:120] or "user"
        username, suffix = base, 1
        while User.objects.filter(username=username).exists():
            username, suffix = f"{base}{suffix}", suffix + 1
        user = User.objects.create_user(username=username, email=email,
                                        password=self.cleaned_data["password1"])
        parts = name.split(maxsplit=1)
        if hasattr(user, "first_name"):
            user.first_name = parts[0] if parts else ""
            user.last_name = parts[1] if len(parts) > 1 else ""
            user.save(update_fields=["first_name", "last_name"])
        return user


class LoopAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email")

    def clean(self):
        email_or_username = self.cleaned_data.get("username", "").strip()

        if email_or_username and "@" in email_or_username:
            try:
                user = User.objects.get(email__iexact=email_or_username)
                self.cleaned_data["username"] = user.get_username()
            except User.DoesNotExist:
                pass

        return super().clean()
