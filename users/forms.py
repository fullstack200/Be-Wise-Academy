from django import forms
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.core.exceptions import ValidationError

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
        fields = UserCreationForm.Meta.fields + ('studentName','grade','parentName','phoneNumber','email','schoolName','syllabus','Physics','Chemistry','Biology','Mathematics','Hindi')
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
        
