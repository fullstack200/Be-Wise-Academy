from django import forms
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

class FeedbackForm(forms.ModelForm):
    studentName = forms.CharField(label='Student Name', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    studentGrade = forms.IntegerField(label='Student Grade [7 to 10]', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Grade'}))
    noOfStars = forms.IntegerField(label='Ratings [1 to 5]', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Ratings'}))
    review = forms.Textarea()           
    feedback = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = Feedback
        fields = '__all__'
       
class EnquiryForm(forms.ModelForm):
    studentName = forms.CharField(label='Student Name', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    phoneNumber = forms.IntegerField(label='Phone Number', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Number'}))
    subject = forms.CharField(label='Subject', 
                    widget=forms.TextInput(attrs={'placeholder': 'Your Subject'}))
    message = forms.Textarea()
    enquiry = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = Enquiry
        fields = '__all__'
        labels = {
            "studentName": _("Student Name"),
            "phoneNumber": _("Phone Number"),
        }
        
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('studentName','grade','parentName','phoneNumber','email','schoolName','syllabus','Physics','Chemistry','Biology','Mathematics','Computer_Science','English','Hindi')
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
        