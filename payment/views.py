from django.shortcuts import render
from datetime import datetime
# Create your views here.

from tutor.models import Fee,Syllabus

from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .models import Payment
from users.models import CustomUser
from django.contrib.auth.decorators import login_required

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
	auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@login_required(login_url='login')
def paymentpage(request):
	currency = 'INR'
	tot_amt = 0

	if request.user.Physics == True:
		syllabus_obj = Syllabus.objects.get(syllabusName=request.user.syllabus)
		fee_obj = Fee.objects.get(syllabus=syllabus_obj,subject="Physics",gradeNumber=request.user.grade)
		tot_amt += fee_obj.fee
	if request.user.Chemistry == True:
		syllabus_obj = Syllabus.objects.get(syllabusName=request.user.syllabus)
		fee_obj = Fee.objects.get(syllabus=syllabus_obj,subject="Chemistry",gradeNumber=request.user.grade)
		tot_amt += fee_obj.fee
	if request.user.Biology == True:
		syllabus_obj = Syllabus.objects.get(syllabusName=request.user.syllabus)
		fee_obj = Fee.objects.get(syllabus=syllabus_obj,subject="Biology",gradeNumber=request.user.grade)
		tot_amt += fee_obj.fee
	if request.user.Hindi == True:
		syllabus_obj = Syllabus.objects.get(syllabusName=request.user.syllabus)
		fee_obj = Fee.objects.get(syllabus=syllabus_obj,subject="Hindi",gradeNumber=request.user.grade)
		tot_amt += fee_obj.fee
		
	amount = tot_amt * 100
	request.session['studentN'] = request.user.studentName
	request.session['amountN'] = amount
		
		# Create a Razorpay Order
	razorpay_order = razorpay_client.order.create(dict(amount=amount,
														currency=currency,
														payment_capture='0'))

		# order id of newly created order.
	razorpay_order_id = razorpay_order['id']
	callback_url = 'paymenthandler/'

		# we need to pass these details to frontend.
	context = {}
	context['amount'] = tot_amt
	context['razorpay_order_id'] = razorpay_order_id
	context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
	context['razorpay_amount'] = amount
	context['currency'] = currency
	context['callback_url'] = callback_url
		
	return render(request, 'payment.html', context=context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
	s = CustomUser.objects.get(studentName=request.session['studentN'])
	a = Payment(student=s,syllabus=s.syllabus,grade=s.grade,amount=request.session['amountN'],paymentStatus=False,paymentDateNTime="0")
	
	a.save()
	# only accept POST request.
	if request.method == "POST":
		
		try:
			# get the required parameters from post request.
			payment_id = request.POST.get('razorpay_payment_id', '')
			razorpay_order_id = request.POST.get('razorpay_order_id', '')
			signature = request.POST.get('razorpay_signature', '')
			params_dict = {
				'razorpay_order_id': razorpay_order_id,
				'razorpay_payment_id': payment_id,
				'razorpay_signature': signature
			}
			# verify the payment signature.
			result = razorpay_client.utility.verify_payment_signature(
				params_dict)
			
			if result is not None:
				amount = request.session['amountN']
				try:
					# capture the payemt
					a.paymentStatus = True
					now = datetime.now()
					current_date = now.strftime("%Y-%m-%d")
					current_time = now.strftime("%H:%M:%S")
					a.paymentDateNTime = current_date +" "+ current_time
					a.save()

					# render success page on successful caputre of payment
				
					context = {'status':True}
					return render(request, 'status.html',context)
				except:
					# if there is an error while capturing payment.
					
					context = {'status':False}
					return render(request, 'status.html',context)
			else:
				# if signature verification fails.
				context = {'status':False}
				return render(request, 'fail.html')
		except:
			# if we don't find the required parameters in POST data
			return HttpResponseBadRequest()
	else:
	# if other than POST request is made.
		return HttpResponseBadRequest()
