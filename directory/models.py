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
