from django import forms

from .models import Website


class ManageWebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ["name", "desc"]
