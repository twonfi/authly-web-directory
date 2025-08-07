from django.db import models
from django.urls import reverse


class Website(models.Model):
    domain = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    desc = models.TextField("description", blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("directory:site_page", kwargs={
            "domain": self.domain,
        })


class Review(models.Model):
    site = models.ForeignKey(Website, on_delete=models.CASCADE)
    reviewer = models.CharField(max_length=255)
    body = models.TextField()
    verified = models.BooleanField('"Verified" review', blank=True,
        help_text="Bring back Fakespot!")
