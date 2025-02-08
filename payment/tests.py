from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutor.models import Fee, Syllabus
from payment.models import Payment
from unittest.mock import patch
from django.utils.timezone import now

User = get_user_model()

class PaymentHandlerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
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

    def test_paymentpage_view(self):
        self.set_session()
        response = self.client.get(reverse('payment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment.html')
        self.assertEqual(response.context['amount'], 9000)
    
    @patch('payment.views.razorpay_client.order.create')
    def test_paymentpage_razorpay_order_creation(self, mock_create_order):
        self.set_session()
        mock_create_order.return_value = {'id': 'test_order_id'}
        response = self.client.get(reverse('payment'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['razorpay_order_id'], 'test_order_id')

    @patch('payment.views.razorpay_client.utility.verify_payment_signature')
    def test_paymenthandler_success(self, mock_verify_signature):
        self.set_session()
        mock_verify_signature.return_value = True
        
        response = self.client.post(reverse('paymenthandler'), {
            'razorpay_payment_id': 'pay_test_123',
            'razorpay_order_id': 'order_test_123',
            'razorpay_signature': 'signature_test_123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'status.html')
        payment = Payment.objects.get(student=self.user)
        self.assertTrue(payment.paymentStatus)
    
    @patch('payment.views.razorpay_client.utility.verify_payment_signature')
    def test_paymenthandler_signature_failure(self, mock_verify_signature):
        self.set_session()
        mock_verify_signature.return_value = None  # Simulate signature failure
        response = self.client.post(reverse('paymenthandler'), {
            'razorpay_payment_id': 'test_payment_id',
            'razorpay_order_id': 'test_order_id',
            'razorpay_signature': 'invalid_signature'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fail.html')
        payment = Payment.objects.get(student=self.user)
        self.assertFalse(payment.paymentStatus)

    def test_paymenthandler_missing_parameters(self):
        self.set_session()
        response = self.client.post(reverse('paymenthandler'), {})
        self.assertEqual(response.status_code, 400)  # Bad request expected

    def test_paymenthandler_get_request(self):
        self.set_session()
        response = self.client.get(reverse('paymenthandler'))
        self.assertEqual(response.status_code, 400)

class PaymentModelTest(TestCase):
    def setUp(self):
        """Set up test data for the Payment model"""
        self.user = User.objects.create_user(
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

        self.payment = Payment.objects.create(
            student=self.user,
            syllabus=self.syllabus.syllabusName,
            grade=str(self.user.grade),
            amount=9000,
            paymentStatus=True,
            paymentDateNTime=str(now())  # Use Django's timezone-aware function
        )

    def test_payment_creation(self):
        """Test that a Payment instance is created correctly"""
        payment = Payment.objects.get(id=self.payment.id)
        self.assertEqual(payment.student, self.user)
        self.assertEqual(payment.syllabus, "CBSE")
        self.assertEqual(payment.grade, "10")
        self.assertEqual(payment.amount, 9000)
        self.assertEqual(payment.paymentStatus, True)
        self.assertTrue(payment.paymentDateNTime)  # Ensures it's not empty

    def test_payment_str_representation(self):
        """Test the __str__ method of Payment model"""
        self.assertEqual(str(self.payment), str(self.user))