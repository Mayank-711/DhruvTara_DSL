# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    grade = models.IntegerField(
        validators=[MinValueValidator(8), MaxValueValidator(12)],
        blank=True, 
        null=True
    )
    
    def __str__(self):
        return self.user.username