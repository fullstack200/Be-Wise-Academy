from django.db import models
import uuid
from django.urls import reverse
import boto3
import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import datetime

# Create your models here.

class Resources(models.Model):
    subjectName = models.CharField(max_length=50)
    topicName = models.CharField(max_length=50)
    document = models.FileField(upload_to="media/docs/")
    uploaded_on = models.DateField(default=datetime.date.today)
    
    def __str__(self):
        return self.topicName

class Syllabus(models.Model):
    syllabusName = models.CharField(max_length=100)

    def __str__(self):
        return self.syllabusName

class Fee(models.Model):
    grade = models.CharField(max_length=100)
    gradeNumber = models.IntegerField(default=10)
    subject = models.CharField(max_length=50)
    fee = models.IntegerField()
    syllabus = models.ForeignKey('Syllabus',on_delete=models.CASCADE)

    def __str__(self):
        return self.grade

class Quiz(models.Model):
    subjectName = models.CharField(max_length=100)
    topicName = models.CharField(max_length=100)
    questionNumber = models.CharField(max_length=100,default="0")
    question = models.TextField()
    questionImage = models.ImageField(null=True,blank=True,upload_to='media/quiz/')
    nameTag = models.CharField(max_length=100,default=0)
    correctAnswer = models.CharField(max_length=1000)

    def __str__(self):
        return self.questionNumber

class mathQuizResult(models.Model):
    studentName = models.CharField(max_length=100)
    subject = models.CharField(default="Mathematics",max_length=50)
    q1 = models.CharField(max_length=100,blank=True, null=True)
    q2 = models.CharField(max_length=100,blank=True, null=True)
    q3 = models.CharField(max_length=100,blank=True, null=True)
    q4 = models.CharField(max_length=100,blank=True, null=True)
    q5 = models.CharField(max_length=100,blank=True, null=True)
    q6 = models.CharField(max_length=100,blank=True, null=True)
    q7 = models.CharField(max_length=100,blank=True, null=True)
    q8 = models.CharField(max_length=100,blank=True, null=True)
    q9 = models.CharField(max_length=100,blank=True, null=True) 
    q10 = models.CharField(max_length=100,blank=True, null=True)
    quizTime = models.CharField(max_length=100,blank=True, null=True)
    correctAnswersCount = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)

    def __str__(self):
        return self.studentName +" "+ self.subject
    
class scienceQuizResult(models.Model):
    studentName = models.CharField(max_length=100)
    subject = models.CharField(default="Science",max_length=50)
    q1 = models.CharField(max_length=100,blank=True, null=True)
    q2 = models.CharField(max_length=100,blank=True, null=True)
    q3 = models.CharField(max_length=100,blank=True, null=True)
    q4 = models.CharField(max_length=100,blank=True, null=True)
    q5 = models.CharField(max_length=100,blank=True, null=True)
    q6 = models.CharField(max_length=100,blank=True, null=True)
    q7 = models.CharField(max_length=100,blank=True, null=True)
    q8 = models.CharField(max_length=100,blank=True, null=True)
    q9 = models.CharField(max_length=100,blank=True, null=True) 
    q10 = models.CharField(max_length=100,blank=True, null=True)
    quizTime = models.CharField(max_length=100,blank=True, null=True)
    correctAnswersCount = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)

    def __str__(self):
        return self.studentName +" "+ self.subject
    
class Blogs(models.Model):
    bid = models.UUIDField( 
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    blogTitle = models.CharField(max_length=100)
    blogAuthor = models.CharField(max_length=50)
    blogUploadDate = models.DateField(default=datetime.date.today)
    blogImage = models.ImageField(upload_to="media/blogs/", height_field=None, width_field=None, max_length=1000)
    blogPara = models.TextField()
    
    def __str__(self):
        return self.blogTitle
        
@receiver(models.signals.post_delete, sender=Resources)
def remove_file_from_s3_resources(sender, instance, using, **kwargs):
    image_fields = ['document']
    for field_name in image_fields:
        # Get the image field value
        image_field = getattr(instance, field_name)
        if image_field:
            # Delete the image file
            image_field.delete(save=False)
            
@receiver(models.signals.post_delete, sender=Blogs)
def remove_file_from_s3_blogs(sender, instance, using, **kwargs):
    image_fields = ['blogImage']
    for field_name in image_fields:
        # Get the image field value
        image_field = getattr(instance, field_name)
        if image_field:
            # Delete the image file
            image_field.delete(save=False)

@receiver(models.signals.post_delete, sender=Quiz)
def remove_file_from_s3_quiz(sender, instance, using, **kwargs):
    image_fields = ['questionImage']
    for field_name in image_fields:
        # Get the image field value
        image_field = getattr(instance, field_name)
        if image_field:
            # Delete the image file
            image_field.delete(save=False)
