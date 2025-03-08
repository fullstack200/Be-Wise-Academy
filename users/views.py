from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import *
from django.http import HttpResponseRedirect
from .forms import *
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages


# Create your views here.

def homePageView(request):
    eform = EnquiryForm()

    if request.method == "POST":
        eform = EnquiryForm(request.POST)
        if eform.is_valid():
            if 'g-recaptcha-response' not in request.POST or not request.POST['g-recaptcha-response'].strip():
                eform.add_error(None, "Please complete the CAPTCHA")
            else:
                eform.save()
                return HttpResponseRedirect(reverse("econfirm"))
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
        if 'enquiry' in request.POST:
            eform = EnquiryForm(request.POST)
            if eform.is_valid():
                if 'g-recaptcha-response' not in request.POST or not request.POST['g-recaptcha-response'].strip():
                    eform.add_error(None, "Please complete the CAPTCHA")
                else:
                    eform.save()
                    return HttpResponseRedirect(reverse('econfirm'))

        elif 'feedback' in request.POST:
            fform = FeedbackForm(request.POST)
            if fform.is_valid():
                if 'g-recaptcha-response' not in request.POST or not request.POST['g-recaptcha-response'].strip():
                    fform.add_error(None, "Please complete the CAPTCHA")
                else:
                    fform.save()
                    return HttpResponseRedirect(reverse('fconfirm'))

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
    success_url = '/confirmed/'
    
class EnquiryFormConfirm(TemplateView):
    template_name = 'enquiryconfirm.html'
    
class FeedbackFormConfirm(TemplateView):
    template_name = 'feedbackconfirm.html'

class SignupConfirm(TemplateView):
    template_name = 'registration/signupconfirm.html'
    
@login_required
def edit_profile(request):
    """Allow users to edit their profile."""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('editconfirm')  # Redirect to profile page after update
    else:
        form = CustomUserChangeForm(instance=request.user)  # Prefill user data

    return render(request, 'registration/edit_profile.html', {'form': form})

class EditConfirm(TemplateView):
    template_name = 'registration/editconfirm.html'
    
class CustomLoginView(LoginView):
    def form_valid(self, form):
        messages.success(self.request, "You have successfully logged in!")
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(self.request, "You have successfully logged out!")
        return super().dispatch(request, *args, **kwargs)
