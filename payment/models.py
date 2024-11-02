from django.db import models
from users.models import CustomUser
import datetime
# Create your models here.


class Payment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    syllabus = models.CharField(max_length=50)
    grade=models.CharField(max_length=50)
    amount = models.IntegerField()
    paymentStatus = models.CharField(max_length=50, default="None")
    paymentDateNTime = models.CharField(max_length=100)

    def __str__(self):
        return str(self.student)