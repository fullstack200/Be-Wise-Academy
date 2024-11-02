from re import template
from urllib import request
from django.shortcuts import render
from django.views.generic import *
from tutor.models import Resources
from django.http import HttpResponseRedirect
from .forms import *
from .models import *

# Create your views here.

def homePageView(request):
    eform = EnquiryForm()

    if request.method == "POST":
        eform = EnquiryForm(request.POST)
        if eform.is_valid():
            eform.save()
            return HttpResponseRedirect("home")
     
    reviews = Feedback.objects.all()
    first_review = reviews[0]
    rest_reviews = reviews[1:]
    
    return render(request, "homepage.html", {"enquiryForm":eform, "first_review":first_review,"rest_reviews":rest_reviews})


class AboutUsPageView(TemplateView):
    template_name = 'about.html'


def contactView(request):
    eform = EnquiryForm()
    fform = FeedbackForm()
     
    if request.method == "POST":
        if 'enquiry' in request.POST:
            eform = EnquiryForm(request.POST)
            if eform.is_valid():
                eform.save()
                return HttpResponseRedirect("contactUs/enquiry_confirm")
            
        elif 'feedback' in request.POST:
            fform = FeedbackForm(request.POST)
            data = request.POST
            print(data)
            if fform.is_valid():
                fform.save()
                return HttpResponseRedirect("contactUs/feedback_confirm")
  
    return render(request, "contact.html", {"cenquiryForm":eform,"feedbackForm":fform})
    
class ServicesPageView(TemplateView):
    template_name = 'services.html'

class ResourcesPageView(TemplateView):
     template_name = 'resources.html'

class EvaluationPageView(TemplateView):
    template_name = 'evaluation.html'
 
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    reviews = Feedback.objects.all()
    first_review = reviews[0]
    rest_reviews = reviews[1:]
    extra_context = {'first_review':first_review,'rest_reviews':rest_reviews}
    success_url = '/'
    
class EnquiryFormConfirm(TemplateView):
    template_name = 'enquiryconfirm.html'
    
class FeedbackFormConfirm(TemplateView):
    template_name = 'feedbackconfirm.html'
