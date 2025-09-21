from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class StudentAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    math_interest = models.IntegerField()
    science_interest = models.IntegerField()
    literature_interest = models.IntegerField()
    coding_interest = models.IntegerField()
    teamwork = models.IntegerField()
    creativity = models.IntegerField()
    helping_interest = models.IntegerField()
    leadership = models.IntegerField()
    travel_interest = models.IntegerField()
    stable_job_interest = models.IntegerField()
    business_interest = models.IntegerField()
    communication_skills = models.IntegerField()

    # Top 3 career choices stored separately
    career_choice_1 = models.CharField(max_length=100)
    career_choice_2 = models.CharField(max_length=100)
    career_choice_3 = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.created_at}"