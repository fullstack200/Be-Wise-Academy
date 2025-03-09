import uuid
import datetime
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.files.storage import default_storage
from users.models import CustomUser

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
            today = datetime.date.today().strftime('%Y%m%d')
            unique_suffix = uuid.uuid4().hex[:6]  # Generate a short unique ID
            self.invoice_number = f"invoice{today}-{unique_suffix}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.invoice_number}"

import logging

logger = logging.getLogger(__name__)  # Add this at the top of your file

@receiver(post_delete, sender=Payment)
def remove_invoice_pdf(sender, instance, **kwargs):
    """Delete the associated invoice PDF from S3 when the Payment object is deleted."""
    if instance.invoice_url:
        try:
            if instance.invoice_url.startswith('https://nbewise.s3.amazonaws.com/'):
                file_path = instance.invoice_url.replace('https://nbewise.s3.amazonaws.com/', '')

            logger.info(f"Attempting to delete file: {file_path}")
            
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                logger.info(f"File {file_path} deleted successfully.")
            else:
                logger.warning(f"File {file_path} not found on S3.")
        except Exception as e:
            logger.error(f"Error deleting invoice file from S3: {e}")
