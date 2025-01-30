from django.test import TestCase
from .models import Feedback, Enquiry, CustomUser
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.forms import CustomUserCreationForm

class FeedbackModelTest(TestCase):
    def test_feedback_creation(self):
        feedback = Feedback.objects.create(
            studentName="John Doe",
            studentGrade=10,
            noOfStars=5,
            review="Great service!"
        )
        self.assertEqual(feedback.studentName, "John Doe")
        self.assertEqual(feedback.studentGrade, 10)
        self.assertEqual(feedback.noOfStars, 5)
        self.assertEqual(feedback.review, "Great service!")
        self.assertEqual(str(feedback), "John Doe")

class EnquiryModelTest(TestCase):
    def test_enquiry_creation(self):
        enquiry = Enquiry.objects.create(
            studentName="Jane Smith",
            phoneNumber=1234567890,
            subject="Math Help",
            message="I need help with calculus."
        )
        self.assertEqual(enquiry.studentName, "Jane Smith")
        self.assertEqual(enquiry.phoneNumber, 1234567890)
        self.assertEqual(enquiry.subject, "Math Help")
        self.assertEqual(enquiry.message, "I need help with calculus.")
        self.assertEqual(str(enquiry), "Jane Smith")

class CustomUserModelTest(TestCase):
    def test_custom_user_invalid_phone_number(self):
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username="invaliduser",
                password="password123",
                studentName="Invalid User",
                grade=10,
                parentName="Mr. Invalid",
                phoneNumber="not_a_number",  # Invalid phone number
                schoolName="Invalid School",
                syllabus="ICSE"
            )
            # Manually call full_clean() to trigger validation
            user.full_clean()  # This will raise a ValidationError because phoneNumber is not an integer

    def test_custom_user_creation(self):
        user = CustomUser.objects.create_user(
            username="testuser",
            password="password123",
            studentName="Alex Brown",
            grade=10,
            parentName="Mrs. Brown",
            phoneNumber=9876543210,
            schoolName="XYZ School",
            syllabus="CBSE"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.studentName, "Alex Brown")
        self.assertEqual(user.grade, 10)
        self.assertEqual(user.parentName, "Mrs. Brown")
        self.assertEqual(user.phoneNumber, 9876543210)
        self.assertEqual(user.schoolName, "XYZ School")
        self.assertEqual(user.syllabus, "CBSE")

    def test_custom_user_syllabus_choice(self):
        user = CustomUser.objects.create_user(
            username="syllabususer",
            password="password123",
            studentName="Syllabus User",
            grade=10,
            parentName="Syllabus Parent",
            phoneNumber=1234567890,
            schoolName="Syllabus School",
            syllabus="IGCSE"
        )
        self.assertEqual(user.syllabus, "IGCSE")

class BasicViewsTest(TestCase):

    def test_about_us_page_view(self):
        response = self.client.get(reverse('about'), follow=True)
        if response.status_code == 301:
            print(response['Location'])  # This will show the redirect destination
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_services_page_view(self):
        response = self.client.get(reverse('services'), follow=True)
        if response.status_code == 301:
            print(response['Location'])  # This will show the redirect destination
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services.html')

    def test_resources_page_view(self):
        response = self.client.get(reverse('resources'), follow=True)
        if response.status_code == 301:
            print(response['Location'])  # This will show the redirect destination
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources.html')

    def test_evaluation_page_view(self):
        response = self.client.get(reverse('evaluation'), follow=True)
        if response.status_code == 301:
            print(response['Location'])  # This will show the redirect destination
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'evaluation.html')

    def test_enquiry_form_confirm_view(self):
        response = self.client.get(reverse('econfirm'), follow=True)
        if response.status_code == 301:
            print(response['Location'])  # This will show the redirect destination
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enquiryconfirm.html')

    def test_feedback_form_confirm_view(self):
        response = self.client.get(reverse('fconfirm'), follow=True)
        if response.status_code == 301:
            print(response['Location'])  # This will show the redirect destination
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feedbackconfirm.html')

class ContactViewTests(TestCase):

    def setUp(self):
        self.contact_url = reverse('contact')  # The URL for the contact page
        self.enquiry_url = reverse('econfirm')
        self.feedback_url = reverse('fconfirm')

    def test_get_contact(self):
        """Test that the contact view renders the contact.html template successfully."""
        response = self.client.get(self.contact_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_post_valid_enquiry_form(self):
        valid_enquiry_data = {
            'studentName': 'Jane Doe',
            'phoneNumber': 1234567890,
            'subject': 'Inquiry about courses',
            'message': 'I would like to know more about the courses offered.',
            'enquiry': True  # Include the hidden field value
        }
        response = self.client.post(reverse('contact'), data=valid_enquiry_data)
    
        # Assert the form is valid and saved
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to 'econfirm'
        self.assertRedirects(response, reverse('econfirm'))  # Check redirection to 'econfirm'
        self.assertTrue(Enquiry.objects.filter(studentName='Jane Doe').exists())  # Verify the record is saved


    def test_post_valid_feedback_form(self):
        valid_feedback_data = {
            'studentName': 'John Doe',
            'studentGrade': 9,
            'noOfStars': 4,
            'review': 'Great experience!',
            'feedback': True  # Include the hidden field value
        }
        response = self.client.post(reverse('contact'), data=valid_feedback_data)
    
        # Assert the form is valid and saved
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to 'fconfirm'
        self.assertRedirects(response, reverse('fconfirm'))  # Check redirection to 'fconfirm'
        self.assertTrue(Feedback.objects.filter(studentName='John Doe').exists())  # Verify the record is saved

    def test_post_invalid_enquiry_form(self):
        # Invalid phone number (less than 10 digits)
        invalid_enquiry_data = {
            'studentName': 'John Doe',
            'phoneNumber': '123456789',  # Invalid phone number (9 digits)
            'subject': 'Test Subject',
            'message': 'Test message content',
            'enquiry': 'True',  # The hidden input, which is required
        }
    
        # Send POST request with invalid data
        response = self.client.post(reverse('contact'), data=invalid_enquiry_data)
        
        # Check that the form is re-rendered with status code 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the form contains the error for the invalid phone number
        self.assertFormError(response, 'cenquiryForm', 'phoneNumber', 'Phone number must be exactly 10 digits long.')
        
        # Ensure that the form is not saved and is still invalid
        self.assertFalse(response.context['cenquiryForm'].is_valid())
    
        # Check that both the enquiry and feedback forms are in the context
        self.assertIn('cenquiryForm', response.context)
        self.assertIn('feedbackForm', response.context)


    def test_post_invalid_feedback_form(self):
        # Invalid student grade (less than 7)
        invalid_feedback_data = {
            'studentName': 'John Doe',
            'studentGrade': 6,  # Invalid student grade (less than 7)
            'noOfStars': 4,  # Valid rating
            'review': 'Test review content',
            'feedback': 'True',  # The hidden input, which is required
        }
    
        # Send POST request with invalid data
        response = self.client.post(reverse('contact'), data=invalid_feedback_data)
        
        # Check that the form is re-rendered with status code 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the form contains the error for the invalid student grade
        self.assertFormError(response, 'feedbackForm', 'studentGrade', 'Student Grade must be between 7 and 10.')
        
        # Ensure that the form is not saved and is still invalid
        self.assertFalse(response.context['feedbackForm'].is_valid())
    
        # Check that both the enquiry and feedback forms are in the context
        self.assertIn('cenquiryForm', response.context)
        self.assertIn('feedbackForm', response.context)


    def test_post_invalid_feedback_rating(self):
        # Invalid rating (greater than 5)
        invalid_feedback_data = {
            'studentName': 'John Doe',
            'studentGrade': 8,  # Valid student grade
            'noOfStars': 6,  # Invalid rating (greater than 5)
            'review': 'Test review content',
            'feedback': 'True',  # The hidden input, which is required
        }
    
        # Send POST request with invalid data
        response = self.client.post(reverse('contact'), data=invalid_feedback_data)
        
        # Check that the form is re-rendered with status code 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the form contains the error for the invalid rating
        self.assertFormError(response, 'feedbackForm', 'noOfStars', 'Ratings must be between 1 and 5.')
        
        # Ensure that the form is not saved and is still invalid
        self.assertFalse(response.context['feedbackForm'].is_valid())
    
        # Check that both the enquiry and feedback forms are in the context
        self.assertIn('cenquiryForm', response.context)
        self.assertIn('feedbackForm', response.context)

    def test_post_without_specifying_form(self):
        # Send a POST request without specifying any form data
        response = self.client.post(reverse('contact'), data={})
    
        # Assert that the response status is 200 (re-rendering the form page)
        self.assertEqual(response.status_code, 200)
    
        # Check that the correct form is rendered in the response context
        self.assertIn('cenquiryForm', response.context)
        self.assertIn('feedbackForm', response.context)
    
        # You might also want to check that no error messages are generated
        self.assertNotContains(response, 'This field is required')  # Example error check

class HomePageViewTests(TestCase):
    
    def test_homepage_view_get(self):
        # Sending a GET request to the homepage
        response = self.client.get(reverse('home'))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'homepage.html')

        # Check that the EnquiryForm is in the context
        self.assertIn('enquiryForm', response.context)

    def test_homepage_view_post_valid_enquiry_form(self):
        # Define valid form data
        valid_enquiry_data = {
            'studentName': 'John Doe',
            'phoneNumber': '1234567890',
            'subject': 'Math',
            'message': 'This is a test message',
            'enquiry': True  # Assuming 'enquiry' field is hidden and set to True
        }

        # Send a POST request to the homepage with the valid enquiry data
        response = self.client.post(reverse('home'), data=valid_enquiry_data)

        # Check that the response is a redirect (302 status code)
        self.assertEqual(response.status_code, 302)

        # Check that the form data was saved by checking the response redirect URL
        self.assertRedirects(response, reverse('home'))

        # Check that the enquiry form was actually saved in the database (optional)
        self.assertEqual(Enquiry.objects.count(), 1)

    def test_homepage_view_post_invalid_enquiry_form(self):
        # Define invalid form data (missing student name)
        invalid_enquiry_data = {
            'studentName': '',
            'phoneNumber': '1234567890',
            'subject': 'Math',
            'message': 'This is a test message',
            'enquiry': True
        }

        # Send a POST request with the invalid enquiry data
        response = self.client.post(reverse('home'), data=invalid_enquiry_data)

        # Check that the response status code is 200 (the form is re-rendered with errors)
        self.assertEqual(response.status_code, 200)

        # Check that the form has errors
        self.assertFormError(response, 'enquiryForm', 'studentName', 'This field is required.')

    def test_homepage_view_no_enquiries_in_db(self):
        # Send a GET request to the homepage when there are no enquiries
        response = self.client.get(reverse('home'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the form is empty and no entries are present in the context (optional)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_homepage_view_with_enquiries_in_db(self):
        # Create a few enquiries in the database
        Enquiry.objects.create(studentName='John Doe', phoneNumber='1234567890', subject='Math', message='This is a test message')
        Enquiry.objects.create(studentName='Jane Smith', phoneNumber='0987654321', subject='Science', message='This is another test message')

        # Send a GET request to the homepage
        response = self.client.get(reverse('home'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Verify that the enquiry form exists in the context
        self.assertIn('enquiryForm', response.context)

        # Verify that the enquiries are stored in the database
        self.assertEqual(Enquiry.objects.count(), 2)

        
CustomUser = get_user_model()

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="securepassword",
            studentName="John Doe",
            grade=9,
            parentName="Jane Doe",
            phoneNumber=9876543210,
            schoolName="XYZ International School",
            syllabus="IGCSE",
            Physics=True,
            Chemistry=False,
            Biology=True,
            Mathematics=True,
            Computer_Science=False,
            English=True,
            Hindi=False,
        )

    def test_user_creation(self):
        """Test if the user is created properly"""
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("securepassword"))
        self.assertEqual(self.user.studentName, "John Doe")
        self.assertEqual(self.user.grade, 9)
        self.assertEqual(self.user.parentName, "Jane Doe")
        self.assertEqual(self.user.phoneNumber, 9876543210)
        self.assertEqual(self.user.schoolName, "XYZ International School")
        self.assertEqual(self.user.syllabus, "IGCSE")

    def test_default_boolean_fields(self):
        """Test if default values of Boolean fields are False"""
        user2 = CustomUser.objects.create_user(
            username="user2", password="anotherpassword",  studentName="John Doe",
            grade=9,
            parentName="Jane Doe",
            phoneNumber=9876543210,
            schoolName="XYZ International School",
            syllabus="IGCSE",
        )
        self.assertFalse(user2.Physics)
        self.assertFalse(user2.Chemistry)
        self.assertFalse(user2.Biology)
        self.assertFalse(user2.Mathematics)
        self.assertFalse(user2.Computer_Science)
        self.assertFalse(user2.English)
        self.assertFalse(user2.Hindi)

    def test_syllabus_choices(self):
        """Test if syllabus choices are valid"""
        self.assertIn(self.user.syllabus, dict(CustomUser.SYLLABUS_CHOICES))

    def test_str_method(self):
        """Test if __str__ method returns username"""
        self.assertEqual(str(self.user), self.user.username)
        
class SignUpViewTest(TestCase):
    def test_signup_page_loads(self):
        """Test if signup page loads properly."""
        response = self.client.get(reverse('signup'))  # Ensure 'signup' is the correct URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_valid_signup(self):
        """Test successful user signup."""
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'studentName': 'John Doe',
            'grade': 10,
            'parentName': 'Jane Doe',
            'phoneNumber': 1234567890,
            'email': 'test@example.com',
            'schoolName': 'ABC High School',
            'syllabus': 'IGCSE',
            'Physics': True,
            'Chemistry': False,
            'Biology': True,
            'Mathematics': False,
            'Computer_Science': True,
            'English': True,
            'Hindi': False,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())

    def test_invalid_signup(self):
        """Test signup failure due to password mismatch."""
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password321',  # Passwords don't match
        })
        self.assertEqual(response.status_code, 200)  # Form reloads due to error
        self.assertContains(response, "The two password fields didn’t match.")  # Django's default error message
        self.assertFalse(CustomUser.objects.filter(username='testuser').exists())  # User should not be created
        
class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        """Test if the form is valid with correct data."""
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'studentName': 'John Doe',
            'grade': 9,
            'parentName': 'Jane Doe',
            'phoneNumber': 9876543210,
            'email': 'test@example.com',
            'schoolName': 'XYZ International',
            'syllabus': 'ICSE',
            'Physics': True,
            'Chemistry': False,
            'Biology': True,
            'Mathematics': False,
            'Computer_Science': True,
            'English': True,
            'Hindi': False,
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_fields(self):
        """Test if form is invalid when required fields are missing."""
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'studentName': '',  # Missing required field
            'grade': '',
            'parentName': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('studentName', form.errors)
        self.assertIn('grade', form.errors)
        self.assertIn('parentName', form.errors)