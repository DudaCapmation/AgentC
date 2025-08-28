from django.db import models

class TeamMember (models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    country = models.CharField(max_length=50)
    joined_on = models.DateField(null=True, blank=True)

class Client (models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)