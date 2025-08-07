from django import forms

from .models import Website, Review


class ManageWebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ["name", "desc"]


class PostReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["reviewer", "body", "verified"]
