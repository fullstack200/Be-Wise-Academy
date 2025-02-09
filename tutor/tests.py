from django.test import TestCase, Client
from .models import *
import uuid
from datetime import date
import datetime
import time
from unittest.mock import patch
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()

class ResourcesModelTest(TestCase):
    def setUp(self):
        """Set up a sample Resources object for testing"""
        self.resource = Resources.objects.create(
            subjectName="Mathematics",
            topicName="Algebra",
            document="media/docs/sample.pdf"
        )

    def test_resource_creation(self):
        """Test if the resource is created successfully"""
        self.assertEqual(self.resource.subjectName, "Mathematics")
        self.assertEqual(self.resource.topicName, "Algebra")
        self.assertEqual(self.resource.document, "media/docs/sample.pdf")
        self.assertEqual(self.resource.uploaded_on, datetime.date.today())

    def test_str_method(self):
        """Test the __str__ method of Resources model"""
        self.assertEqual(str(self.resource), "Algebra")
        
    @patch('django.db.models.fields.files.FieldFile.delete')  # Mock file deletion
    def test_s3_file_deletion_on_resource_delete(self, mock_delete):
        """Test if the file is deleted from S3 when a resource is deleted"""

        # Create a mock resource with an S3-stored file
        resource = Resources.objects.create(
            subjectName="Science",
            topicName="Physics",
            document="media/docs/sample.pdf"
        )

        # Delete the resource
        resource.delete()

        # Check if the file delete method was called
        mock_delete.assert_called_once_with(save=False)
        
class SyllabusModelTest(TestCase):
    def test_syllabus_creation(self):
        syllabus = Syllabus.objects.create(syllabusName="CBSE")
        self.assertEqual(str(syllabus), "CBSE")

class FeeModelTest(TestCase):
    def setUp(self):
        self.syllabus = Syllabus.objects.create(syllabusName="ICSE")

    def test_fee_creation(self):
        fee = Fee.objects.create(
            grade="10th Grade",
            gradeNumber=10,
            subject="Mathematics",
            fee=5000,
            syllabus=self.syllabus
        )
        self.assertEqual(str(fee), "10th Grade")
        self.assertEqual(fee.syllabus.syllabusName, "ICSE")

class BlogListViewTest(TestCase):

    def setUp(self):
        """Create sample blog entries for testing."""
        Blogs.objects.create(blogTitle="First Blog", blogAuthor="Author 1", blogPara="Content of the first blog.")
        Blogs.objects.create(blogTitle="Second Blog", blogAuthor="Author 2", blogPara="Content of the second blog.")

    def test_blog_list_view(self):
        """Test that the blog list view displays the correct blogs."""
        url = reverse('blogList')  # Make sure this URL is correct
        response = self.client.get(url)

        # Ensure the context contains 'blogs' if context_object_name is set in the view
        blogs = Blogs.objects.all().order_by('blogUploadDate')  # Order by any field you want

        # Assert that the correct number of blogs is rendered in the response
        self.assertEqual(len(response.context['blogs']), len(blogs))

        # Assert that the titles of the blogs match the expected titles in order
        for blog, expected_blog in zip(response.context['blogs'], blogs):
            self.assertEqual(blog.blogTitle, expected_blog.blogTitle)

class BlogDetailViewTest(TestCase):

    def setUp(self):
        """Set up test data"""
        # Create a dummy image file for the blog
        image_data = SimpleUploadedFile(name="test_image.jpg", content=b"image_data", content_type="image/jpeg")
        
        self.blog = Blogs.objects.create(
            blogTitle="Sample Blog",
            blogAuthor="Author 1",
            blogUploadDate="2025-01-01",
            blogImage=image_data,
            blogPara="This is the content of the blog"
        )

    def test_blog_detail_view(self):
        """Test that the blog detail view retrieves the correct blog based on bid"""
        url = reverse('blogDetail', kwargs={'bid': self.blog.bid})  # Update with actual URL name and `bid`
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)  # Check for successful response (HTTP 200)
        self.assertContains(response, "Sample Blog")  # Check if the blog title is in the response
        self.assertContains(response, "This is the content of the blog")  # Check if the content is in the response
        self.assertEqual(response.context['blog'], self.blog)  # Ensure the correct blog is passed in context

class QuizModelTest(TestCase):
    def test_quiz_creation(self):
        quiz = Quiz.objects.create(
            subjectName="Science",
            topicName="Physics",
            questionNumber="1",
            question="What is Newton's First Law?",
            nameTag="Forces",
            correctAnswer="An object in motion stays in motion"
        )
        self.assertEqual(str(quiz), "1")
        
    @patch('django.db.models.fields.files.FieldFile.delete')  # Mock file deletion
    def test_s3_file_deletion_on_quiz_delete(self, mock_delete):
        """Test if the questionImage file is deleted from S3 when a quiz is deleted"""

        # Create a mock quiz with an S3-stored image
        quiz = Quiz.objects.create(
            subjectName="Math",
            topicName="Algebra",
            question="What is x in x+2=4?",
            questionImage="media/quiz/sample.png"
        )

        # Delete the quiz
        quiz.delete()

        # Check if the file delete method was called
        mock_delete.assert_called_once_with(False)

class MathQuizResultModelTest(TestCase):
    def test_math_quiz_result_creation(self):
        result = mathQuizResult.objects.create(
            studentName="John Doe",
            correctAnswersCount=8,
            percentage=80.0
        )
        self.assertEqual(str(result), "John Doe Mathematics")
        self.assertEqual(result.correctAnswersCount, 8)
        self.assertEqual(result.percentage, 80.0)

class ScienceQuizResultModelTest(TestCase):
    def test_science_quiz_result_creation(self):
        result = scienceQuizResult.objects.create(
            studentName="Jane Doe",
            correctAnswersCount=7,
            percentage=70.0
        )
        self.assertEqual(str(result), "Jane Doe Science")
        self.assertEqual(result.correctAnswersCount, 7)
        self.assertEqual(result.percentage, 70.0)

class BlogsModelTest(TestCase):

    def setUp(self):
        """Set up a sample blog instance for testing."""
        self.blog = Blogs.objects.create(
            blogTitle="Test Blog",
            blogAuthor="John Doe",
            blogUploadDate=datetime.date.today(),
            blogImage="media/blogs/sample.jpg",
            blogPara="This is a test blog."
        )

    def test_blog_creation(self):
        """Test if the blog is created successfully."""
        self.assertEqual(Blogs.objects.count(), 1)
        self.assertEqual(self.blog.blogTitle, "Test Blog")
        self.assertIsInstance(self.blog.bid, uuid.UUID)

    def test_blog_str_method(self):
        """Test the __str__ method of the Blog model."""
        self.assertEqual(str(self.blog), "Test Blog")

    @patch('django.db.models.fields.files.FieldFile.delete')  # Mock file deletion
    def test_s3_file_deletion_on_blog_delete(self, mock_delete):
        """Test if the blogImage file is deleted from S3 when a blog is deleted"""

        # Delete the blog
        self.blog.delete()

        # Check if the file delete method was called
        mock_delete.assert_called_once_with(False)
        
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from tutor.models import Syllabus, Resources, Fee

User = get_user_model()

class TutorAppViewsTest(TestCase):
    def setUp(self):
        """Set up test data including user login"""
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='teststudent',
            password='testpassword',
            studentName='John Doe',
            grade=10,
            parentName='Jane Doe',
            phoneNumber=1234567890,
            schoolName='Test School',
            syllabus='CBSE',
            Physics=True, Chemistry=False, Biology=True, Mathematics=True, Hindi=False
        )
        
        # Log in the user before tests
        self.client.login(username='teststudent', password='testpassword')

        # Create syllabus data
        self.syllabus1 = Syllabus.objects.create(syllabusName="IGCSE")
        self.syllabus2 = Syllabus.objects.create(syllabusName="CBSE")

        # Create test file for upload
        test_file = SimpleUploadedFile("test.pdf", b"This is a test document.", content_type="application/pdf")

        # Create Resources for Subjects with file
        Resources.objects.create(subjectName="Physics", topicName="Mechanics", document=test_file)
        Resources.objects.create(subjectName="Chemistry", topicName="Organic", document=test_file)
        Resources.objects.create(subjectName="Biology", topicName="Cells", document=test_file)
        Resources.objects.create(subjectName="Mathematics", topicName="Algebra", document=test_file)

        # Create Fee Data
        Fee.objects.create(grade="7th IGCSE", gradeNumber=7, subject="Math", fee=5000, syllabus=self.syllabus1)
        Fee.objects.create(grade="8th IGCSE", gradeNumber=8, subject="Science", fee=5500, syllabus=self.syllabus1)
        Fee.objects.create(grade="9th CBSE", gradeNumber=9, subject="Physics", fee=6000, syllabus=self.syllabus2)

    def test_physics_view(self):
        """Test Physics View fetches Physics resources"""
        url = reverse('physics')  # Update with actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mechanics")
        self.assertContains(response, "test.pdf")  # Ensuring file is present

    def test_chemistry_view(self):
        """Test Chemistry View fetches Chemistry resources"""
        url = reverse('chemistry')  # Update with actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organic")
        self.assertContains(response, "test.pdf")

    def test_mathematics_view(self):
        """Test Mathematics View fetches Mathematics resources"""
        url = reverse('mathematics')  # Update with actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Algebra")
        self.assertContains(response, "test.pdf")

    def test_fee_view(self):
        """Test Fee View fetches correct fee details"""
        url = reverse('price') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 5000)
        self.assertContains(response, 6000)
        
class QuizModelTest(TestCase):

    def setUp(self):
        """Set up test data for Quiz model."""
        self.quiz = Quiz.objects.create(
            subjectName="Mathematics",
            topicName="Algebra",
            questionNumber="1",
            question="What is 2 + 2?",
            questionImage=None,
            nameTag="Math_Algebra_1",
            correctAnswer="4",
        )

    def test_quiz_model_creation(self):
        """Test the creation of a Quiz object and validate the fields."""
        quiz = self.quiz
        self.assertEqual(quiz.subjectName, "Mathematics")
        self.assertEqual(quiz.topicName, "Algebra")
        self.assertEqual(quiz.questionNumber, "1")
        self.assertEqual(quiz.question, "What is 2 + 2?")
        self.assertEqual(quiz.correctAnswer, "4")
        self.assertEqual(quiz.nameTag, "Math_Algebra_1")
        self.assertFalse(quiz.questionImage)    # Assuming no image is provided in this case

    def test_quiz_string_representation(self):
        """Test the string representation of the Quiz object."""
        self.assertEqual(str(self.quiz), "1")  # Since questionNumber is "1"

    def test_quiz_invalid_data(self):
        """Test invalid data handling."""
        with self.assertRaises(ValidationError):
            # Creating a quiz object without a required field
            quiz = Quiz(subjectName="", topicName="Algebra", questionNumber="1", question="What is 2 + 2?", correctAnswer="4")
            quiz.full_clean()  # This should raise a ValidationError because subjectName is required

    def test_quiz_image_field(self):
        """Test if the quiz image field is optional and handles null values correctly."""
        quiz = Quiz.objects.create(
            subjectName="Science",
            topicName="Physics",
            questionNumber="2",
            question="What is the speed of light?",
            correctAnswer="299792458 m/s",
            nameTag="Science_Physics_2",
            questionImage=None  # Image field is left empty (null)
        )
        self.assertFalse(quiz.questionImage)    # Image field is correctly null

class MathScienceResultModelTest(TestCase):
    def setUp(self):
        """Set up sample data for math and science quiz results."""
        # Create 10 questions for both Math and Science quizzes
        for i in range(1, 11):
            Quiz.objects.create(subjectName="Mathematics", topicName="Topic " + str(i), 
                                questionNumber=str(i), question=f"Math Question {i}", 
                                correctAnswer=f"Answer {i}")
            Quiz.objects.create(subjectName="Science", topicName="Topic " + str(i), 
                                questionNumber=str(i), question=f"Science Question {i}", 
                                correctAnswer=f"Answer {i}")
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Create mathQuizResult and scienceQuizResult for a student (assuming a student "John Doe")
        self.math_result = mathQuizResult.objects.create(
            studentName="John Doe",
            q1="Answer 1", q2="Answer 2", q3="Answer 3", q4="Answer 4", q5="Answer 5", 
            q6="Answer 6", q7="Answer 7", q8="Answer 8", q9="Answer 9", q10="Answer 10",
            quizTime=f"Quiz taken at {current_time}"
        )

        self.science_result = scienceQuizResult.objects.create(
            studentName="John Doe",
            q1="Answer 1", q2="Answer 2", q3="Answer 3", q4="Answer 4", q5="Answer 5", 
            q6="Answer 6", q7="Answer 7", q8="Answer 8", q9="Answer 9", q10="Answer 10",
            quizTime=f"Quiz taken at {current_time}"
        )

    def test_math_result_creation(self):
        """Test that the math quiz result is correctly saved."""
        result_object = mathQuizResult.objects.get(studentName="John Doe")

        # Check that all answers are correctly saved
        self.assertEqual(result_object.q1, "Answer 1")
        self.assertEqual(result_object.q10, "Answer 10")

        # Check default subject is Mathematics
        self.assertEqual(result_object.subject, "Mathematics")

        # Check that correctAnswersCount is initially 0
        self.assertEqual(result_object.correctAnswersCount, 0)

        # Check that percentage is initially 0
        self.assertEqual(result_object.percentage, 0)

    def test_science_result_creation(self):
        """Test that the science quiz result is correctly saved."""
        result_object = scienceQuizResult.objects.get(studentName="John Doe")

        # Check that all answers are correctly saved
        self.assertEqual(result_object.q1, "Answer 1")
        self.assertEqual(result_object.q10, "Answer 10")

        # Check default subject is Science
        self.assertEqual(result_object.subject, "Science")

        # Check that correctAnswersCount is initially 0
        self.assertEqual(result_object.correctAnswersCount, 0)

        # Check that percentage is initially 0
        self.assertEqual(result_object.percentage, 0)

    def test_correct_answers_count_for_math_quiz(self):
        """Test that correct answers count is calculated properly in mathQuizResult."""
        # Simulate the result for math quiz
        correct_answers = [f"Answer {i}" for i in range(1, 11)]
        user_answers = [self.math_result.q1, self.math_result.q2, self.math_result.q3, 
                        self.math_result.q4, self.math_result.q5, self.math_result.q6, 
                        self.math_result.q7, self.math_result.q8, self.math_result.q9, 
                        self.math_result.q10]
        
        boolList = []
        for i in range(10):
            if user_answers[i].lower() == correct_answers[i].lower():
                boolList.append(True)
        
        correctAnswersCount = boolList.count(True)
        self.math_result.correctAnswersCount = correctAnswersCount
        self.math_result.percentage = correctAnswersCount / 10 * 100
        self.math_result.save()

        # Check that the correctAnswersCount is correctly updated to 10
        self.assertEqual(self.math_result.correctAnswersCount, 10)

        # Check that the percentage is correctly calculated as 100%
        self.assertEqual(self.math_result.percentage, 100)

    def test_correct_answers_count_for_science_quiz(self):
        """Test that correct answers count is calculated properly in scienceQuizResult."""
        # Simulate the result for science quiz
        correct_answers = [f"Answer {i}" for i in range(1, 11)]
        user_answers = [self.science_result.q1, self.science_result.q2, self.science_result.q3, 
                        self.science_result.q4, self.science_result.q5, self.science_result.q6, 
                        self.science_result.q7, self.science_result.q8, self.science_result.q9, 
                        self.science_result.q10]
        
        boolList = []
        for i in range(10):
            if user_answers[i].lower() == correct_answers[i].lower():
                boolList.append(True)
        
        correctAnswersCount = boolList.count(True)
        self.science_result.correctAnswersCount = correctAnswersCount
        self.science_result.percentage = correctAnswersCount / 10 * 100
        self.science_result.save()

        # Check that the correctAnswersCount is correctly updated to 10
        self.assertEqual(self.science_result.correctAnswersCount, 10)

        # Check that the percentage is correctly calculated as 100%
        self.assertEqual(self.science_result.percentage, 100)

    def test_quiz_time_format(self):
        """Test that the quizTime is formatted correctly with date and time."""
        current_date = date.today()
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        # Test quizTime for math and science results
        self.assertIn("at", self.math_result.quizTime)
        self.assertIn(current_date.strftime("%Y-%m-%d"), self.math_result.quizTime)
        self.assertIn(current_time, self.math_result.quizTime)

        self.assertIn("at", self.science_result.quizTime)
        self.assertIn(current_date.strftime("%Y-%m-%d"), self.science_result.quizTime)
        self.assertIn(current_time, self.science_result.quizTime)

########################################################################################################

    def test_wrong_answer(self):
        """Test that wrong answers are counted correctly."""
        # Simulate wrong answers for math quiz (e.g., changing q1 and q2 to wrong answers)
        self.math_result.q1 = "Wrong Answer 1"
        self.math_result.q2 = "Wrong Answer 2"
        self.math_result.save()

        correct_answers = [f"Answer {i}" for i in range(1, 11)]
        user_answers = [self.math_result.q1, self.math_result.q2, self.math_result.q3, 
                        self.math_result.q4, self.math_result.q5, self.math_result.q6, 
                        self.math_result.q7, self.math_result.q8, self.math_result.q9, 
                        self.math_result.q10]
        
        boolList = []
        for i in range(10):
            if user_answers[i].lower() == correct_answers[i].lower():
                boolList.append(True)

        correctAnswersCount = boolList.count(True)
        self.math_result.correctAnswersCount = correctAnswersCount
        self.math_result.percentage = correctAnswersCount / 10 * 100
        self.math_result.save()

        # Check that the correctAnswersCount is correctly updated (should be 8 if q1 and q2 are wrong)
        self.assertEqual(self.math_result.correctAnswersCount, 8)

        # Check that the percentage is correctly calculated (should be 80% if 8 answers are correct)
        self.assertEqual(self.math_result.percentage, 80)

    def test_blank_answer(self):
        """Test that blank answers are counted as incorrect."""
        # Simulate blank answers for math quiz (e.g., setting some answers to blank)
        self.math_result.q1 = ""
        self.math_result.q2 = ""
        self.math_result.save()

        correct_answers = [f"Answer {i}" for i in range(1, 11)]
        user_answers = [self.math_result.q1, self.math_result.q2, self.math_result.q3, 
                        self.math_result.q4, self.math_result.q5, self.math_result.q6, 
                        self.math_result.q7, self.math_result.q8, self.math_result.q9, 
                        self.math_result.q10]
        
        boolList = []
        for i in range(10):
            if user_answers[i] == "":  # Blank answer logic
                boolList.append(False)  # Treat blank as incorrect
            elif user_answers[i].lower() == correct_answers[i].lower():
                boolList.append(True)

        correctAnswersCount = boolList.count(True)
        self.math_result.correctAnswersCount = correctAnswersCount
        self.math_result.percentage = correctAnswersCount / 10 * 100
        self.math_result.save()

        # Check that the correctAnswersCount is correctly updated (should be 8 if 2 answers are blank)
        self.assertEqual(self.math_result.correctAnswersCount, 8)

        # Check that the percentage is correctly calculated (should be 80% if 8 answers are correct)
        self.assertEqual(self.math_result.percentage, 80)
        
class QuizReviewViewsTest(TestCase):

    def setUp(self):
        """Set up sample data for quiz review tests."""
        # Create sample questions for both Math and Science quizzes
        for i in range(1, 11):
            Quiz.objects.create(subjectName="Mathematics", topicName="Topic " + str(i), 
                                questionNumber=str(i), question=f"Math Question {i}", 
                                correctAnswer=f"Answer {i}")
            Quiz.objects.create(subjectName="Science", topicName="Topic " + str(i), 
                                questionNumber=str(i), question=f"Science Question {i}", 
                                correctAnswer=f"Answer {i}")

        # Create quiz results for a student (no need for user authentication)
        self.math_result = mathQuizResult.objects.create(
            studentName="John Doe",
            q1="Answer 1", q2="Answer 2", q3="Answer 3", q4="Answer 4", q5="Answer 5", 
            q6="Answer 6", q7="Answer 7", q8="Answer 8", q9="Answer 9", q10="Answer 10",
            quizTime="Quiz taken at 2025-01-01 10:00:00"
        )

        self.science_result = scienceQuizResult.objects.create(
            studentName="John Doe",
            q1="Answer 1", q2="Answer 2", q3="Answer 3", q4="Answer 4", q5="Answer 5", 
            q6="Answer 6", q7="Answer 7", q8="Answer 8", q9="Answer 9", q10="Answer 10",
            quizTime="Quiz taken at 2025-01-01 10:00:00"
        )

    def test_math_questions_review(self):
        """Test the mathQuestionsReview view."""
        # Use a sample name in place of request.session['name']
        sample_name = "John Doe"
        
        # Manually set session data
        session = self.client.session
        session['name'] = sample_name
        session.save()  # Ensure the session is saved

        # Now request the view
        response = self.client.get(reverse('math-test-review'))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "test-review.html")

        # Check if correct data is passed to the template
        context = response.context
        self.assertIn('questions', context)
        self.assertIn('result_object', context)
        self.assertIn('boolList', context)

        # Check if boolean list corresponds to correct answers
        correct_answers = [f"Answer {i}" for i in range(1, 11)]
        user_answers = [self.math_result.q1, self.math_result.q2, self.math_result.q3,
                        self.math_result.q4, self.math_result.q5, self.math_result.q6,
                        self.math_result.q7, self.math_result.q8, self.math_result.q9,
                        self.math_result.q10]
        bool_list = []
        for i in range(10):
            if user_answers[i] == None:
                bool_list.append(None)
            elif correct_answers[i].lower() == user_answers[i].lower():
                bool_list.append(True)
            else:
                bool_list.append(False)

        self.assertEqual(context['boolList'], bool_list)

    def test_science_questions_review(self):
        """Test the scienceQuestionsReview view."""
        # Use a sample name in place of request.session['name']
        sample_name = "John Doe"
        
        # Manually set session data
        session = self.client.session
        session['name'] = sample_name
        session.save()  # Ensure the session is saved

        # Now request the view
        response = self.client.get(reverse('science-test-review'))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "test-review.html")

        # Check if correct data is passed to the template
        context = response.context
        self.assertIn('questions', context)
        self.assertIn('result_object', context)
        self.assertIn('boolList', context)

        # Check if boolean list corresponds to correct answers
        correct_answers = [f"Answer {i}" for i in range(1, 11)]
        user_answers = [self.science_result.q1, self.science_result.q2, self.science_result.q3,
                        self.science_result.q4, self.science_result.q5, self.science_result.q6,
                        self.science_result.q7, self.science_result.q8, self.science_result.q9,
                        self.science_result.q10]
        bool_list = []
        for i in range(10):
            if user_answers[i] == None:
                bool_list.append(None)
            elif correct_answers[i].lower() == user_answers[i].lower():
                bool_list.append(True)
            else:
                bool_list.append(False)

        self.assertEqual(context['boolList'], bool_list)