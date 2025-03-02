from django.db import models
from users.models import CustomUser
import datetime
import uuid

class Payment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    syllabus = models.CharField(max_length=50)
    grade = models.CharField(max_length=50)
    amount = models.IntegerField()
    paymentStatus = models.BooleanField(default=False)
    paymentDateNTime = models.CharField(max_length=100)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True, default="")
    invoice_url = models.URLField(max_length=500, blank=True, null=True)  # New field to store invoice URL

    def save(self, *args, **kwargs):
        """Generate a unique invoice number before saving"""
        if not self.invoice_number:
            today = datetime.date.today().strftime('%d%m')
            unique_suffix = uuid.uuid4().hex[:6]  # Generate a short unique ID
            self.invoice_number = f"invoice{today}-{unique_suffix}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.invoice_number}"
