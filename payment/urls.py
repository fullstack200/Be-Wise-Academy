from django.urls import path
from payment import views

urlpatterns = [
	path('payment/', views.paymentpage, name='payment'),
	path('payment/paymenthandler/', views.paymenthandler, name='paymenthandler'),
]
