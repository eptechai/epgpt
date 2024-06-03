from pyexpat import model
import uuid

from django.db import models

# Create your models here.


class Company(models.Model):
    company_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    company_name = models.CharField(null=False, blank=False, unique=True, max_length=20)


class Campaign(models.Model):
    campaign_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    campaign_name = models.CharField(null=False, blank=False, unique=True, max_length=20)
    campaign_status = models.BooleanField(default=True)
    campaign_company = models.ForeignKey(
        "Company", null=False, blank=False, on_delete=models.CASCADE
    )

