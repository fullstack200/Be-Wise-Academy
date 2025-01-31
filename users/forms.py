from django import forms
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.core.exceptions import ValidationError
import re

class FeedbackForm(forms.ModelForm):
    studentName = forms.CharField(label='Student Name', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    
    # Validate studentGrade to be between 7 and 10
    studentGrade = forms.IntegerField(
        label='Student Grade [7 to 10]', 
        widget=forms.TextInput(attrs={'placeholder': 'Your Grade'})
    )
    
    # Validate noOfStars to be between 0 and 5
    noOfStars = forms.IntegerField(
        label='Ratings [1 to 5]', 
        widget=forms.TextInput(attrs={'placeholder': 'Your Ratings'})
    )

    review = forms.Textarea()
    feedback = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = Feedback
        fields = '__all__'

    def clean_studentGrade(self):
        grade = self.cleaned_data.get('studentGrade')
        if grade < 7 or grade > 10:
            raise ValidationError('Student Grade must be between 7 and 10.')
        return grade

    def clean_noOfStars(self):
        stars = self.cleaned_data.get('noOfStars')
        if stars < 1 or stars > 5:
            raise ValidationError('Ratings must be between 1 and 5.')
        return stars

class EnquiryForm(forms.ModelForm):
    studentName = forms.CharField(label='Student Name', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    
    phoneNumber = forms.IntegerField(
        label='Phone Number', 
        widget=forms.TextInput(attrs={'placeholder': 'Your Number'})
    )
    
    subject = forms.CharField(label='Subject', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Subject'}))
    message = forms.Textarea()
    enquiry = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = Enquiry
        fields = '__all__'

    def clean_phoneNumber(self):
        phone_number = str(self.cleaned_data.get('phoneNumber'))
        if len(phone_number) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        return phone_number

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'studentName', 'grade', 'parentName', 'phoneNumber', 'email',
            'schoolName', 'syllabus', 'Physics', 'Chemistry', 'Biology', 'Mathematics', 'Hindi'
        )

    def clean_studentName(self):
        """Ensure name contains only alphabets and spaces."""
        studentName = self.cleaned_data.get('studentName')
        if not re.match(r'^[A-Za-z ]+$', studentName):
            raise ValidationError("Student name should only contain letters and spaces.")
        return studentName

    def clean_parentName(self):
        """Ensure parent name contains only alphabets and spaces."""
        parentName = self.cleaned_data.get('parentName')
        if not re.match(r'^[A-Za-z ]+$', parentName):
            raise ValidationError("Parent name should only contain letters and spaces.")
        return parentName

    def clean_grade(self):
        """Ensure grade is between 7 and 10."""
        grade = self.cleaned_data.get('grade')
        if not (7 <= grade <= 10):
            raise ValidationError("Grade must be between 7 and 10.")
        return grade

    def clean_phoneNumber(self):
        """Ensure phone number is exactly 10 digits."""
        phoneNumber = self.cleaned_data.get('phoneNumber')
        if not re.match(r'^\d{10}$', str(phoneNumber)):
            raise ValidationError("Phone number must be exactly 10 digits and contain only numbers.")
        return phoneNumber

    def clean_email(self):
        """Ensure email is valid."""
        email = self.cleaned_data.get('email')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure no field (except subjects) is left blank
        required_fields = [
            'username', 'password1', 'password2', 'studentName', 'grade',
            'parentName', 'phoneNumber', 'email', 'schoolName', 'syllabus'
        ]
        
        for field in required_fields:
            if not cleaned_data.get(field):
                raise ValidationError({field: f"{field.replace('_', ' ').capitalize()} cannot be empty."})
        
        # Ensure at least one subject is selected
        subjects = [
            cleaned_data.get('Physics'),
            cleaned_data.get('Chemistry'),
            cleaned_data.get('Biology'),
            cleaned_data.get('Mathematics'),
            cleaned_data.get('Computer_Science'),
            cleaned_data.get('English'),
            cleaned_data.get('Hindi')
        ]
        
        if not any(subjects):
            raise ValidationError("At least one subject must be selected.")

        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            'studentName', 'grade', 'parentName', 'phoneNumber', 'email', 
            'schoolName', 'syllabus', 'Physics', 'Chemistry', 'Biology', 
            'Mathematics', 'Computer_Science', 'English', 'Hindi'
        )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide the password field from the form
        if 'password' in self.fields:
            del self.fields['password']

    def clean_phoneNumber(self):
        """Ensure phone number is 10 digits."""
        phone_number = self.cleaned_data.get("phoneNumber")
        if not str(phone_number).isdigit() or len(str(phone_number)) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_number

    def clean_grade(self):
        """Ensure grade is between 7 and 10."""
        grade = self.cleaned_data.get("grade")
        if grade < 7 or grade > 10:
            raise forms.ValidationError("Grade must be between 7 and 10.")
        return grade
        
