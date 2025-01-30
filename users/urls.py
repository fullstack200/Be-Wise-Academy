from django.urls import path
from .views import *

urlpatterns = [
    path('aboutUs/', AboutUsPageView.as_view(), name='about'),
    path('', homePageView, name='home'),
    path('contactUs/', contactView, name='contact'),
    path('contactUs/enquiry_confirm/',EnquiryFormConfirm.as_view(),name='econfirm'),
    path('contactUs/feedback_confirm/',FeedbackFormConfirm.as_view(),name='fconfirm'),
    path('services/', ServicesPageView.as_view(), name='services'),
    path('resources/', ResourcesPageView.as_view(), name='resources'),
    path('evaluation/', EvaluationPageView.as_view(), name='evaluation'),
    path('signup/',SignUpView.as_view(),name='signup'),
    path('confirmed/', SignupConfirm.as_view(), name='signupconfirm' )
]
