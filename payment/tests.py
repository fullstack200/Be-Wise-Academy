from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from payment.models import Payment
from tutor.models import Fee, Syllabus
import datetime
from django.utils import timezone
from .views import generate_invoice_pdf
from users.models import CustomUser
import fitz
import boto3
from io import BytesIO
from botocore.exceptions import NoCredentialsError
import os
import calendar
import logging

logger = logging.getLogger(__name__)

# class PaymentInvoicePageTests(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = get_user_model().objects.create_user(
#             username='teststudent',
#             password='testpassword',
#             studentName='John Doe',
#             grade=10,
#             parentName='Jane Doe',
#             phoneNumber=1234567890,
#             schoolName='Test School',
#             syllabus='CBSE',
#             Physics=True, Chemistry=False, Biology=True, Hindi=False
#         )
        
#         self.syllabus = Syllabus.objects.create(syllabusName='CBSE')
#         Fee.objects.create(syllabus=self.syllabus, subject='Physics', gradeNumber=10, fee=5000)
#         Fee.objects.create(syllabus=self.syllabus, subject='Biology', gradeNumber=10, fee=4000)
        
#         self.client.login(username='teststudent', password='testpassword')

#     def set_session(self):
#         """ Manually set session variables. """
#         session = self.client.session
#         session['studentN'] = self.user.studentName
#         session['amountN'] = 900000  # Amount stored in session (in paise)
#         session.save()

#     @patch('payment.views.razorpay_client.order.create')
#     def test_payment_invoice_page_success(self, mock_razorpay):
#         """ Test successful payment invoice page rendering. """
#         self.set_session()
        
#         mock_razorpay.return_value = {'id': 'order_123'}
        
#         response = self.client.get(reverse('payment'))
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context['amount'], 9000)
#         self.assertEqual(response.context['razorpay_order_id'], 'order_123')
#         self.assertEqual(self.client.session['studentN'], 'John Doe')
#         self.assertEqual(self.client.session['amountN'], 900000)

#     def test_access_without_login(self):
#         """ Test access control - Unauthenticated users should be redirected. """
#         self.client.logout()
#         response = self.client.get(reverse('payment'))
#         self.assertRedirects(response, '/login/?next=/payment/')

#     def test_invoice_number_auto_generation(self):
#         """ Test `invoice_number` is auto-generated if not provided. """
#         payment = Payment.objects.create(
#             student=self.user,
#             syllabus='CBSE',
#             grade='10',
#             amount=9000,
#             paymentStatus=True,
#             paymentDateNTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         )

#         self.assertIsNotNone(payment.invoice_number)
#         self.assertTrue(payment.invoice_number.startswith('invoice'))

#     def test_invoice_url_handling(self):
#         """ Test that `invoice_url` is optional and can be blank. """
#         payment = Payment.objects.create(
#             student=self.user,
#             syllabus='CBSE',
#             grade='10',
#             amount=8000,
#             paymentStatus=True,
#             paymentDateNTime='2023-09-25 10:00:00',
#             invoice_url=''
#         )

#         self.assertEqual(payment.invoice_url, '')

#     def test_invoice_grouping_by_year_and_month(self):
#         """ Test invoices are grouped correctly by year and month. """
        
#         # Create Payment entries with specific invoice URLs and dates (formatted as invoiceYYYYDDMM)
#         Payment.objects.create(
#             student=self.user, 
#             invoice_url='invoices/invoice20230308-xyz.pdf',  # March 8, 2023
#             amount=9000, 
#             paymentDateNTime=timezone.now()
#         )
#         Payment.objects.create(
#             student=self.user, 
#             invoice_url='invoices/invoice20230510-abc.pdf',  # May 10, 2023
#             amount=8000, 
#             paymentDateNTime=timezone.now()
#         )
#         Payment.objects.create(
#             student=self.user, 
#             invoice_url='invoices/invoice20231225-def.pdf',  # December 25, 2023
#             amount=7000, 
#             paymentDateNTime=timezone.now()
#         )

#         # Simulate view logic to group invoices by year and month
#         invoices_by_year = {}
        
#         payments = Payment.objects.all()
#         for payment in payments:
#             invoice_url = payment.invoice_url
#             if invoice_url:
#                 try:
#                     filename = invoice_url.split('/')[-1]  # Extract filename
#                     date_part = filename.replace('invoice', '')[:8]  # Extract YYYYDDMM

#                     year, day, month_number = int(date_part[:4]), int(date_part[4:6]), int(date_part[6:])
#                     month_name = calendar.month_name[month_number]
#                     month_year_key = f"{month_name} {year}"

#                     if year not in invoices_by_year:
#                         invoices_by_year[year] = {}

#                     if month_year_key not in invoices_by_year[year]:
#                         invoices_by_year[year][month_year_key] = []

#                     invoices_by_year[year][month_year_key].append({
#                         'day': day,
#                         'month': month_name,
#                         'year': year,
#                         'url': invoice_url
#                     })

#                 except Exception as e:
#                     logger.error(f"Error parsing invoice: {e}")
        
#         # Check if the invoices are grouped by year
#         self.assertIn(2023, invoices_by_year)

#         # Check if the invoices are grouped correctly by month and year
#         self.assertIn('March 2023', invoices_by_year[2023])
#         self.assertIn('May 2023', invoices_by_year[2023])
#         self.assertIn('December 2023', invoices_by_year[2023])

#         # Check if the invoices are correctly assigned to the proper month and day
#         self.assertEqual(invoices_by_year[2023]['March 2023'][0]['day'], 8)
#         self.assertEqual(invoices_by_year[2023]['May 2023'][0]['day'], 10)
#         self.assertEqual(invoices_by_year[2023]['December 2023'][0]['day'], 25)

#         # Check if the invoice URLs are correctly assigned
#         self.assertEqual(invoices_by_year[2023]['March 2023'][0]['url'], 'invoices/invoice20230308-xyz.pdf')
#         self.assertEqual(invoices_by_year[2023]['May 2023'][0]['url'], 'invoices/invoice20230510-abc.pdf')
#         self.assertEqual(invoices_by_year[2023]['December 2023'][0]['url'], 'invoices/invoice20231225-def.pdf')

#     @patch('payment.views.razorpay_client.order.create')
#     def test_razorpay_order_creation_failure(self, mock_create_order):
#         # Mock Razorpay client to raise an exception
#         mock_create_order.side_effect = Exception("Razorpay error")

#         response = self.client.get(reverse('payment'))

#         # Assert the page still loads without crashing
#         self.assertEqual(response.status_code, 200)
#         self.assertNotContains(response, 'razorpay_order_id')  # Ensure order ID is not shown
    

#     def test_missing_amount_raises_error(self):
#         """ Test that missing `amount` raises an error. """
#         with self.assertRaises(Exception):
#             Payment.objects.create(
#                 student=self.user,
#                 syllabus='CBSE',
#                 grade='10',
#                 paymentStatus=True,
#                 paymentDateNTime='2023-09-25 10:00:00'
#             )


# from django.test import TestCase
# from unittest.mock import patch, Mock
# import io
# from .views import generate_invoice_pdf  # Adjust the import path as needed

# class GenerateInvoicePdfTests(TestCase):

#     @patch("boto3.client")
#     def test_s3_pdf_download_failure(self, mock_s3_client):
#         # Mock S3 client
#         mock_s3 = Mock()
#         mock_s3_client.return_value = mock_s3

#         # Simulate empty PDF file download
#         empty_file = io.BytesIO()
#         mock_s3.download_fileobj.side_effect = lambda bucket, key, file_obj: file_obj.write(empty_file.getvalue())

#         # Mock payment object with minimal required data
#         class MockPayment:
#             invoice_number = "INV-001"
#             amount = 1000
#             student = Mock(studentName="John Doe", syllabus="Science", grade=10)

#         payment = MockPayment()

#         # Assert the function raises a ValueError
#         with self.assertRaisesMessage(ValueError, "Downloaded PDF file is empty or corrupted."):
#             generate_invoice_pdf(payment)
            
#     @patch("boto3.client")
#     def test_invalid_pdf_file(self, mock_s3_client):
#         # Mock S3 client
#         mock_s3 = Mock()
#         mock_s3_client.return_value = mock_s3

#         # Simulate corrupted PDF file download (missing '%PDF' header)
#         corrupted_pdf = io.BytesIO(b"This is not a valid PDF file")
#         mock_s3.download_fileobj.side_effect = lambda bucket, key, file_obj: file_obj.write(corrupted_pdf.getvalue())

#         # Mock payment object with minimal required data
#         class MockPayment:
#             invoice_number = "INV-002"
#             amount = 1500
#             student = Mock(studentName="Jane Doe", syllabus="Math", grade=11)

#         payment = MockPayment()

#         # Assert the function raises a ValueError
#         with self.assertRaisesMessage(ValueError, "Downloaded PDF data is invalid or corrupted."):
#             generate_invoice_pdf(payment)

#     @patch("boto3.client")
#     def test_montserrat_font_download_failure(self, mock_s3_client):
#         # Mock S3 client
#         mock_s3 = Mock()
#         mock_s3_client.return_value = mock_s3

#         # Simulate valid PDF file download
#         valid_pdf = io.BytesIO(b"%PDF-1.7\nValid PDF Content")
#         mock_s3.download_fileobj.side_effect = lambda bucket, key, file_obj: (
#             file_obj.write(valid_pdf.getvalue()) if "invoice_template.pdf" in key
#             else file_obj.write(b"")  # Simulate empty/corrupted font file
#         )

#         # Mock payment object with minimal required data
#         class MockPayment:
#             invoice_number = "INV-003"
#             amount = 2000
#             student = Mock(studentName="Alice", syllabus="Physics", grade=12)

#         payment = MockPayment()

#         # Assert the function raises a ValueError
#         with self.assertRaisesMessage(ValueError, "Downloaded font file is empty or corrupted."):
#             generate_invoice_pdf(payment)
    
    # @patch("boto3.client")
    # def test_successful_invoice_generation(self, mock_s3_client):
    #     # Setup for testing
    #     mock_s3 = patch("boto3.client").start()
        
    #     # S3 configuration and file paths (adjust based on your environment)
    #     s3 = boto3.client(
    #         "s3",
    #         aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),  # or use settings
    #         aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),  # or use settings
    #         region_name=os.getenv("AWS_S3_REGION_NAME")  # or use settings
    #     )
        
    #     # Test S3 Bucket and Paths
    #     bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
    #     template_s3_key = "static/invoice_template.pdf"  # S3 Path
    #     font_s3_key = "static/fonts/Montserrat-Regular.ttf"

    #     # Simulate real download from S3
    #     pdf_file = io.BytesIO()
    #     font_file = io.BytesIO()

    #     # Download PDF and Font files from S3
    #     try:
    #         s3.download_fileobj(bucket_name, template_s3_key, pdf_file)
    #         s3.download_fileobj(bucket_name, font_s3_key, font_file)
    #     except NoCredentialsError:
    #         self.fail("Credentials are not set up properly.")
        
    #     # Check if the downloaded PDF file is empty
    #     if pdf_file.getbuffer().nbytes == 0:
    #         self.fail("Downloaded PDF file is empty.")
        
    #     pdf_file.seek(0)
    #     font_file.seek(0)

    #     # Create a mock CustomUser object for the student (with all relevant fields)
    #     student = CustomUser.objects.create(
    #         username="bob_student",
    #         email="bob@example.com",
    #         password="password123",  # Add other fields as necessary based on your CustomUser model
    #         studentName="Bob Student",
    #         grade=10,  # Grade as integer
    #         parentName="John Doe",
    #         phoneNumber=1234567890,
    #         schoolName="ABC High School",
    #         syllabus="IGCSE",  # Choose one of the available options
    #         Physics=True,  # Assuming the student has opted for Physics
    #         Chemistry=True,  # Assuming the student has opted for Chemistry
    #         Biology=False,  # Assuming the student has not opted for Biology
    #         Mathematics=True,  # Assuming the student has opted for Mathematics
    #         Hindi=True  # Assuming the student has opted for Hindi
    #     )

    #     # Create the Payment object with all required attributes
    #     payment = Payment.objects.create(
    #         student=student,
    #         syllabus="IGCSE",
    #         grade="10th",  # Grade as string (you can choose which field you want to use)
    #         amount=3000,
    #         paymentStatus=True,
    #         paymentDateNTime="2025-03-08 12:00:00",
    #         invoice_number="INV-004",
    #         invoice_url=""  # Will be updated by the generate_invoice_pdf function
    #     )

    #     # Mock S3 upload method to check if it's called properly
    #     mock_s3.upload_fileobj = patch("boto3.client.upload_fileobj", return_value=None).start()

    #     # Run the function to generate the invoice
    #     try:
    #         invoice_url = generate_invoice_pdf(payment)
    #     except ValueError as e:
    #         self.fail(f"Invoice generation failed: {e}")

    #     # Assertions
    #     mock_s3.upload_fileobj.assert_called_once()  # Ensure it was uploaded
    #     self.assertIn("https://", invoice_url)  # Verify the URL format
    #     self.assertTrue(invoice_url.startswith("https://"))  # Check if it starts with the correct domain

    #     # Ensure invoice_url is updated in the payment
    #     payment.refresh_from_db()  # Make sure the payment object has been updated with the URL
    #     self.assertEqual(payment.invoice_url, invoice_url)  # Confirm the invoice URL was saved


######################################## Works fine ##########################################################
# from unittest.mock import patch
# from django.test import TestCase
# from payment.models import Payment  
# import uuid
# import datetime


# class PaymentTestCase(TestCase):
#     @patch('django.core.files.storage.default_storage.delete')  # Mock S3 delete method
#     @patch('django.core.files.storage.default_storage.exists')  # Mock S3 exists method
#     def test_s3_file_deletion_on_payment_delete(self, mock_exists, mock_delete):
#         """Test if the invoice file is deleted from S3 when a Payment object is deleted"""

#         # Create a mock Payment object with an invoice URL
#         payment = Payment.objects.create(
#             student_id=1,  # Assuming you have a CustomUser with ID 1
#             syllabus="Math",
#             grade="A",
#             amount=1000,
#             paymentStatus=True,
#             paymentDateNTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             invoice_number=f"invoice{datetime.date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
#             invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20250803-44aa880a.pdf"
#         )

#         # Mock the exists method to return True, simulating that the file exists on S3
#         mock_exists.return_value = True

#         # Delete the Payment object
#         payment.delete()

#         # Get the relative file path from the URL
#         file_path = payment.invoice_url.replace('https://nbewise.s3.amazonaws.com/', '')

#         # Check if the delete method was called with the correct file path
#         mock_delete.assert_called_once_with(file_path)

#     @patch('django.core.files.storage.default_storage.delete')  # Mock S3 delete method
#     @patch('django.core.files.storage.default_storage.exists')  # Mock S3 exists method
#     def test_s3_file_not_deleted_if_not_found(self, mock_exists, mock_delete):
#         """Test if the file is not deleted from S3 if it doesn't exist"""

#         # Create a mock Payment object with an invoice URL
#         payment = Payment.objects.create(
#             student_id=1,  # Assuming you have a CustomUser with ID 1
#             syllabus="Math",
#             grade="A",
#             amount=1000,
#             paymentStatus=True,
#             paymentDateNTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             invoice_number=f"invoice{datetime.date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
#             invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20250803-44aa880a.pdf"
#         )

#         # Mock the exists method to return False, simulating that the file doesn't exist on S3
#         mock_exists.return_value = False

#         # Delete the Payment object
#         payment.delete()

#         # Get the relative file path from the URL
#         file_path = payment.invoice_url.replace('https://nbewise.s3.amazonaws.com/', '')

#         # Check if the delete method was not called since the file doesn't exist
#         mock_delete.assert_not_called()
