from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Feedback(models.Model):
    studentName = models.CharField(max_length=50)
    studentGrade = models.IntegerField()
    noOfStars = models.IntegerField()
    review = models.TextField()

    def __str__(self):
        return self.studentName[:50]


class Enquiry(models.Model):
    studentName = models.CharField(max_length=50)
    phoneNumber = models.IntegerField()
    subject = models.CharField(max_length=50)
    message = models.TextField()

    def __str__(self):
        return self.studentName[:50]


class CustomUser(AbstractUser):
    SYLLABUS_CHOICES = (
        ('IGCSE', 'IGCSE'),
        ('International Baccalaureate', 'International Baccalaureate'),
        ('ICSE', 'ICSE'),
        ('CBSE', 'CBSE')
    )
    studentName = models.CharField(max_length=50)
    grade = models.IntegerField()
    parentName = models.CharField(max_length=50)
    phoneNumber = models.IntegerField()
    schoolName = models.CharField(max_length=50)
    syllabus = models.CharField(choices=SYLLABUS_CHOICES, max_length=50)
    Physics = models.BooleanField(default=False)
    Chemistry = models.BooleanField(default=False)
    Biology = models.BooleanField(default=False)
    Mathematics = models.BooleanField(default=False)
    Computer_Science = models.BooleanField(default=False)
    English = models.BooleanField(default=False)
    Hindi = models.BooleanField(default=False)

