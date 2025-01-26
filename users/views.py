from re import template
from urllib import request
from django.shortcuts import render, redirect
from django.urls import reverse

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
            return HttpResponseRedirect(reverse("home"))
     
    reviews = Feedback.objects.all()
    first_review = reviews[0] if reviews else None
    rest_reviews = reviews[1:] if len(reviews) > 1 else []

    
    return render(request, "homepage.html", {"enquiryForm":eform, "first_review":first_review,"rest_reviews":rest_reviews})


class AboutUsPageView(TemplateView):
    template_name = 'about.html'


def contactView(request):
    eform = EnquiryForm()
    fform = FeedbackForm()
    
    if request.method == "POST":
        # Check for 'enquiry' form submission
        if 'enquiry' in request.POST:
            eform = EnquiryForm(request.POST)
            if eform.is_valid():
                eform.save()
                return HttpResponseRedirect(reverse('econfirm'))
            else:
                return render(request, "contact.html", {"cenquiryForm": eform, "feedbackForm": fform})

        # Check for 'feedback' form submission
        elif 'feedback' in request.POST:
            fform = FeedbackForm(request.POST)
            if fform.is_valid():
                fform.save()
                return HttpResponseRedirect(reverse('fconfirm'))
            else:
                return render(request, "contact.html", {"cenquiryForm": eform, "feedbackForm": fform})

    return render(request, "contact.html", {"cenquiryForm": eform, "feedbackForm": fform})
    
class ServicesPageView(TemplateView):
    template_name = 'services.html'

class ResourcesPageView(TemplateView):
     template_name = 'resources.html'

class EvaluationPageView(TemplateView):
    template_name = 'evaluation.html'
 
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = '/'
    
class EnquiryFormConfirm(TemplateView):
    template_name = 'enquiryconfirm.html'
    
class FeedbackFormConfirm(TemplateView):
    template_name = 'feedbackconfirm.html'
