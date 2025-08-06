from django import forms

from .models import Challenge


class LoginForm(forms.ModelForm):
    domain = forms.RegexField(label="Domain name", max_length=255,
        regex=r"[a-z0-9-.]+")

    class Meta:
        model = Challenge
        fields = ("domain",)
