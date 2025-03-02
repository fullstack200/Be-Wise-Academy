from django.urls import path
from payment import views

urlpatterns = [
	path('payment/', views.payment_invoice_page, name='payment'),
	path('payment/paymenthandler/', views.paymenthandler, name='paymenthandler'),
]
