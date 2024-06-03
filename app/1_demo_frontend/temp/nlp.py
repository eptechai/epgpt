from pyexpat import model
import uuid

from django.db import models

# Create your models here.


class NLPModel(models.Model):
    model_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    model_name = models.CharField(null=False, blank=False, unique=True, max_length=20)
    model_version = models.IntegerField(null=False, blank=False, unique=True)
    model_storage = models.CharField(null=False, blank=False, unique=True)
    model_filename = models.CharField(null=False, blank=False, unique=True)

class NLPDatabase(models.Model):
    database_url = models.CharField(null=False, blank=False, unique=True)
    database_port = models.CharField(null=False, blank=False, unique=True)





