from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from payment.models import Payment
from tutor.models import Fee, Syllabus
import datetime
from django.utils import timezone
from .views import generate_invoice_pdf
import calendar
import logging
from django.test import TestCase
from unittest.mock import patch, Mock
import io
from .views import generate_invoice_pdf 
import uuid
import datetime
from .invoice_generator import generate_invoice_pdf
from users.models import CustomUser

logger = logging.getLogger(__name__)

class PaymentInvoicePageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='teststudent',
            password='testpassword',
            studentName='John Doe',
            grade=10,
            parentName='Jane Doe',
            phoneNumber=1234567890,
            schoolName='Test School',
            syllabus='CBSE',
            Physics=True, Chemistry=False, Biology=True, Hindi=False
        )
        
        self.syllabus = Syllabus.objects.create(syllabusName='CBSE')
        Fee.objects.create(syllabus=self.syllabus, subject='Physics', gradeNumber=10, fee=5000)
        Fee.objects.create(syllabus=self.syllabus, subject='Biology', gradeNumber=10, fee=4000)
        
        self.client.login(username='teststudent', password='testpassword')

    def set_session(self):
        """ Manually set session variables. """
        session = self.client.session
        session['studentN'] = self.user.studentName
        session['amountN'] = 900000  # Amount stored in session (in paise)
        session.save()

    @patch('payment.views.razorpay_client.order.create')
    def test_payment_invoice_page_success(self, mock_razorpay):
        """ Test successful payment invoice page rendering. """
        self.set_session()
        
        mock_razorpay.return_value = {'id': 'order_123'}
        
        response = self.client.get(reverse('payment'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['amount'], 9000)
        self.assertEqual(response.context['razorpay_order_id'], 'order_123')
        self.assertEqual(self.client.session['studentN'], 'John Doe')
        self.assertEqual(self.client.session['amountN'], 900000)

    def test_access_without_login(self):
        """ Test access control - Unauthenticated users should be redirected. """
        self.client.logout()
        response = self.client.get(reverse('payment'))
        self.assertRedirects(response, '/login/?next=/payment/')

    def test_invoice_number_auto_generation(self):
        """ Test `invoice_number` is auto-generated if not provided. """
        payment = Payment.objects.create(
            student=self.user,
            syllabus='CBSE',
            grade='10',
            amount=9000,
            paymentStatus=True,
            paymentDateNTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        self.assertIsNotNone(payment.invoice_number)
        self.assertTrue(payment.invoice_number.startswith('invoice'))

    def test_invoice_url_handling(self):
        """ Test that `invoice_url` is optional and can be blank. """
        payment = Payment.objects.create(
            student=self.user,
            syllabus='CBSE',
            grade='10',
            amount=8000,
            paymentStatus=True,
            paymentDateNTime='2023-09-25 10:00:00',
            invoice_url=''
        )

        self.assertEqual(payment.invoice_url, '')

    def test_invoice_grouping_by_year_and_month(self):
        """ Test invoices are grouped correctly by year and month. """
        # Create Payment entries with updated invoice URLs in YYYYMMDD format
        Payment.objects.create(
            student=self.user, 
            invoice_url='invoices/invoice20230308-xyz.pdf',  # March 8, 2023
            amount=9000, 
            paymentDateNTime=timezone.now()
        )
        Payment.objects.create(
            student=self.user, 
            invoice_url='invoices/invoice20230510-abc.pdf',  # May 10, 2023
            amount=8000, 
            paymentDateNTime=timezone.now()
        )
        Payment.objects.create(
            student=self.user, 
            invoice_url='invoices/invoice20231225-def.pdf',  # December 25, 2023
            amount=7000, 
            paymentDateNTime=timezone.now()
        )

        # Simulate view logic to group invoices by year and month
        invoices_by_year = {}
        
        payments = Payment.objects.all()
        for payment in payments:
            invoice_url = payment.invoice_url
            if invoice_url:
                try:
                    filename = invoice_url.split('/')[-1]  # Extract filename
                    date_part = filename.replace('invoice', '')[:8]  # Extract YYYYMMDD

                    year, month_number, day = int(date_part[:4]), int(date_part[4:6]), int(date_part[6:])
                    month_name = calendar.month_name[month_number]
                    month_year_key = f"{month_name} {year}"

                    if year not in invoices_by_year:
                        invoices_by_year[year] = {}

                    if month_year_key not in invoices_by_year[year]:
                        invoices_by_year[year][month_year_key] = []

                    invoices_by_year[year][month_year_key].append({
                        'day': day,
                        'month': month_name,
                        'year': year,
                        'url': invoice_url
                    })

                except Exception as e:
                    logger.error(f"Error parsing invoice: {e}")
        
        # Assertions
        self.assertIn(2023, invoices_by_year)
        self.assertIn('March 2023', invoices_by_year[2023])
        self.assertIn('May 2023', invoices_by_year[2023])
        self.assertIn('December 2023', invoices_by_year[2023])

        # Day Assertions
        self.assertEqual(invoices_by_year[2023]['March 2023'][0]['day'], 8)
        self.assertEqual(invoices_by_year[2023]['May 2023'][0]['day'], 10)
        self.assertEqual(invoices_by_year[2023]['December 2023'][0]['day'], 25)

        # URL Assertions
        self.assertEqual(invoices_by_year[2023]['March 2023'][0]['url'], 'invoices/invoice20230308-xyz.pdf')
        self.assertEqual(invoices_by_year[2023]['May 2023'][0]['url'], 'invoices/invoice20230510-abc.pdf')
        self.assertEqual(invoices_by_year[2023]['December 2023'][0]['url'], 'invoices/invoice20231225-def.pdf')

    @patch('payment.views.razorpay_client.order.create')
    def test_razorpay_order_creation_failure(self, mock_create_order):
        # Mock Razorpay client to raise an exception
        mock_create_order.side_effect = Exception("Razorpay error")

        response = self.client.get(reverse('payment'))

        # Assert the page still loads without crashing
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'razorpay_order_id')  # Ensure order ID is not shown
    

    def test_missing_amount_raises_error(self):
        """ Test that missing `amount` raises an error. """
        with self.assertRaises(Exception):
            Payment.objects.create(
                student=self.user,
                syllabus='CBSE',
                grade='10',
                paymentStatus=True,
                paymentDateNTime='2023-09-25 10:00:00'
            )

######################################## Works fine ##########################################################
from unittest.mock import patch
from django.test import TestCase
from payment.models import Payment  
import uuid
import datetime


class PaymentTestCase(TestCase):
    @patch('django.core.files.storage.default_storage.delete')  # Mock S3 delete method
    @patch('django.core.files.storage.default_storage.exists')  # Mock S3 exists method
    def test_s3_file_deletion_on_payment_delete(self, mock_exists, mock_delete):
        """Test if the invoice file is deleted from S3 when a Payment object is deleted"""

        # Create a mock Payment object with an invoice URL
        payment = Payment.objects.create(
            student_id=1,  # Assuming you have a CustomUser with ID 1
            syllabus="Math",
            grade="A",
            amount=1000,
            paymentStatus=True,
            paymentDateNTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            invoice_number=f"invoice{datetime.date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
            invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20250803-44aa880a.pdf"
        )

        # Mock the exists method to return True, simulating that the file exists on S3
        mock_exists.return_value = True

        # Delete the Payment object
        payment.delete()

        # Get the relative file path from the URL
        file_path = payment.invoice_url.replace('https://nbewise.s3.amazonaws.com/', '')

        # Check if the delete method was called with the correct file path
        mock_delete.assert_called_once_with(file_path)

    @patch('django.core.files.storage.default_storage.delete')  # Mock S3 delete method
    @patch('django.core.files.storage.default_storage.exists')  # Mock S3 exists method
    def test_s3_file_not_deleted_if_not_found(self, mock_exists, mock_delete):
        """Test if the file is not deleted from S3 if it doesn't exist"""

        # Create a mock Payment object with an invoice URL
        payment = Payment.objects.create(
            student_id=1,  # Assuming you have a CustomUser with ID 1
            syllabus="Math",
            grade="A",
            amount=1000,
            paymentStatus=True,
            paymentDateNTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            invoice_number=f"invoice{datetime.date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
            invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20250803-44aa880a.pdf"
        )

        # Mock the exists method to return False, simulating that the file doesn't exist on S3
        mock_exists.return_value = False

        # Delete the Payment object
        payment.delete()

        # Get the relative file path from the URL
        file_path = payment.invoice_url.replace('https://nbewise.s3.amazonaws.com/', '')

        # Check if the delete method was not called since the file doesn't exist
        mock_delete.assert_not_called()

class PaymentHandlerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='teststudent',
            password='testpassword',
            studentName='John Doe',
            grade=10,
            parentName='Jane Doe',
            phoneNumber=1234567890,
            schoolName='Test School',
            syllabus='CBSE',
            Physics=True, Chemistry=False, Biology=True, Hindi=False
        )
        self.payment_url = reverse('paymenthandler')  # Assuming 'paymenthandler' is the URL name

    @patch('payment.views.razorpay_client.utility.verify_payment_signature')
    @patch('payment.views.generate_invoice_pdf')
    def test_successful_payment(self, mock_generate_invoice_pdf, mock_verify_signature):
        """Test successful payment flow with proper data and signature verification."""
        mock_verify_signature.return_value = True
        mock_generate_invoice_pdf.return_value = 'invoices/invoice20230925-xyz.pdf'

        session = self.client.session
        session['studentN'] = self.user.studentName
        session['amountN'] = 90000
        session.save()

        data = {
            'razorpay_payment_id': 'payment123',
            'razorpay_order_id': 'order123',
            'razorpay_signature': 'signature123'
        }

        response = self.client.post(self.payment_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'status.html')
        self.assertContains(response, 'invoices/invoice20230925-xyz.pdf')

        payment = Payment.objects.get(student=self.user)
        self.assertTrue(payment.paymentStatus)
        self.assertEqual(payment.amount, 900)
        self.assertEqual(payment.invoice_url, 'invoices/invoice20230925-xyz.pdf')

    @patch('payment.views.razorpay_client.utility.verify_payment_signature')
    def test_failed_payment_due_to_signature_verification(self, mock_verify_signature):
        """Test payment failure due to signature mismatch."""
        mock_verify_signature.return_value = False

        session = self.client.session
        session['studentN'] = self.user.studentName
        session['amountN'] = 90000
        session.save()

        data = {
            'razorpay_payment_id': 'payment123',
            'razorpay_order_id': 'order123',
            'razorpay_signature': 'wrong_signature'
        }

        response = self.client.post(self.payment_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fail.html')

        payment = Payment.objects.get(student=self.user)
        self.assertFalse(payment.paymentStatus)

    def test_post_request_with_missing_data(self):
        """Test POST request with incomplete data."""
        session = self.client.session
        session['studentN'] = self.user.studentName
        session['amountN'] = 90000
        session.save()

        data = {
            'razorpay_payment_id': 'payment123'  # Missing order_id and signature
        }

        response = self.client.post(self.payment_url, data)
        self.assertEqual(response.status_code, 400)  # Bad request expected

    def test_non_post_request(self):
        """Test GET request to ensure non-POST requests are rejected."""
        session = self.client.session
        session['studentN'] = self.user.studentName  # Add session data
        session.save()

        response = self.client.get(self.payment_url)
#         self.assertEqual(response.status_code, 400)  # Bad request expected

class GenerateInvoicePdfTests(TestCase):
    
    @patch("boto3.client")
    def test_s3_pdf_download_failure(self, mock_s3_client):
        mock_s3 = Mock()
        mock_s3_client.return_value = mock_s3

        empty_file = io.BytesIO()
        mock_s3.download_fileobj.side_effect = lambda bucket, key, file_obj: file_obj.write(empty_file.getvalue())

        class MockPayment:
            invoice_number = "INV-001"
            amount = 1000
            student = Mock(studentName="John Doe", syllabus="Science", grade=10)

        payment = MockPayment()

        with self.assertRaisesMessage(ValueError, "Downloaded PDF file is empty or corrupted."):
            generate_invoice_pdf(payment)
            
    @patch("boto3.client")
    def test_invalid_pdf_file(self, mock_s3_client):
        mock_s3 = Mock()
        mock_s3_client.return_value = mock_s3

        corrupted_pdf = io.BytesIO(b"This is not a valid PDF file")
        mock_s3.download_fileobj.side_effect = lambda bucket, key, file_obj: file_obj.write(corrupted_pdf.getvalue())

        class MockPayment:
            invoice_number = "INV-002"
            amount = 1500
            student = Mock(studentName="Jane Doe", syllabus="Math", grade=11)

        payment = MockPayment()

        with self.assertRaisesMessage(ValueError, "Downloaded PDF data is invalid or corrupted."):
            generate_invoice_pdf(payment)

    @patch("boto3.client")
    def test_montserrat_font_download_failure(self, mock_s3_client):
        mock_s3 = Mock()
        mock_s3_client.return_value = mock_s3

        valid_pdf = io.BytesIO(b"%PDF-1.7\nValid PDF Content")
        mock_s3.download_fileobj.side_effect = lambda bucket, key, file_obj: (
            file_obj.write(valid_pdf.getvalue()) if "invoice_template.pdf" in key
            else file_obj.write(b"")
        )

        class MockPayment:
            invoice_number = "INV-003"
            amount = 2000
            student = Mock(studentName="Alice", syllabus="Physics", grade=12)

        payment = MockPayment()

        with self.assertRaisesMessage(ValueError, "Downloaded font file is empty or corrupted."):
            generate_invoice_pdf(payment)


class PaymentModelTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user( username='teststudent',
            password='testpassword',
            studentName='John Doe',
            grade=10,
            parentName='Jane Doe',
            phoneNumber=1234567890,
            schoolName='Test School',
            syllabus='CBSE',
            Physics=True, Chemistry=False, Biology=True, Hindi=False)

    def test_invoice_number_generated_on_save(self):
        payment = Payment.objects.create(
            student=self.user,
            syllabus="Science",
            grade="10",
            amount=1000
        )
        self.assertTrue(payment.invoice_number.startswith("invoice"))
        self.assertEqual(len(payment.invoice_number.split('-')[-1]), 6)  # UUID suffix check

    def test_invoice_url_is_saved(self):
        payment = Payment.objects.create(
            student=self.user,
            syllabus="Math",
            grade="11",
            amount=2000,
            invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20240925-abc123.pdf"
        )
        self.assertEqual(payment.invoice_url, "https://nbewise.s3.amazonaws.com/invoices/invoice20240925-abc123.pdf")

class RemoveInvoicePdfTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user( username='teststudent',
            password='testpassword',
            studentName='John Doe',
            grade=10,
            parentName='Jane Doe',
            phoneNumber=1234567890,
            schoolName='Test School',
            syllabus='CBSE',
            Physics=True, Chemistry=False, Biology=True, Hindi=False)
        
    @patch('django.core.files.storage.default_storage.exists')
    @patch('django.core.files.storage.default_storage.delete')
    def test_remove_invoice_pdf_success(self, mock_delete, mock_exists):
        # Mock file existence
        mock_exists.return_value = True  

        payment = Payment.objects.create(
            student=self.user,
            syllabus="Science",
            grade="10",
            amount=1000,
            invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20240925-xyz789.pdf"
        )

        # Trigger deletion
        payment.delete()

        # Assert file deletion was attempted
        mock_delete.assert_called_once_with('invoices/invoice20240925-xyz789.pdf')

    @patch('django.core.files.storage.default_storage.exists')
    @patch('django.core.files.storage.default_storage.delete')
    def test_remove_invoice_pdf_file_not_found(self, mock_delete, mock_exists):
        # Mock file non-existence
        mock_exists.return_value = False  

        payment = Payment.objects.create(
            student=self.user,
            syllabus="History",
            grade="12",
            amount=3000,
            invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20240925-zzz999.pdf"
        )

        # Trigger deletion
        payment.delete()

        # Assert deletion wasn't called since the file doesn't exist
        mock_delete.assert_not_called()

    @patch('django.core.files.storage.default_storage.exists')
    @patch('django.core.files.storage.default_storage.delete')
    def test_remove_invoice_pdf_no_invoice_url(self, mock_delete, mock_exists):
        payment = Payment.objects.create(
            student=self.user,
            syllabus="English",
            grade="9",
            amount=500,
            invoice_url=None
        )

        # Trigger deletion
        payment.delete()

        # Assert no file deletion attempts occurred
        mock_delete.assert_not_called()

    @patch('django.core.files.storage.default_storage.exists')
    @patch('django.core.files.storage.default_storage.delete')
    def test_remove_invoice_pdf_error_handling(self, mock_delete, mock_exists):
        mock_exists.side_effect = Exception("Unexpected error occurred")

        payment = Payment.objects.create(
            student=self.user,
            syllabus="Math",
            grade="8",
            amount=750,
            invoice_url="https://nbewise.s3.amazonaws.com/invoices/invoice20240925-error999.pdf"
        )

        # Trigger deletion
        with self.assertLogs('payment.models', level='ERROR') as log:  # Replace 'app.models' with your app's name
            payment.delete()

        self.assertIn("Error deleting invoice file from S3", log.output[0])

