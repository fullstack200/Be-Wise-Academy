from django.shortcuts import render
from datetime import datetime
from tutor.models import Fee,Syllabus
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .models import Payment
from users.models import CustomUser
from django.contrib.auth.decorators import login_required
import fitz
import os
from django.http import FileResponse
import logging
import io
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

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

def generate_invoice_pdf(payment):
    """Generate an invoice PDF for the given payment."""
    
    # 🔹 Step 1: Initialize S3 Client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    template_s3_key = "static/invoice_template.pdf"  # S3 Path
    file_stream = io.BytesIO()  # In-memory file
    s3.download_fileobj(settings.AWS_STORAGE_BUCKET_NAME, template_s3_key, file_stream)
    file_stream.seek(0)  # Reset pointer

    # 🔹 Step 2: Load PDF Template
    doc = fitz.open(stream=file_stream, filetype="pdf")
    page = doc[0]

    # 🔹 Step 3: Define Static Text Positions
    text_positions = {
        "date": (167, 662),  # <CUURENT DATE>
        "invoice_number": (161, 624),  # <INVOICE NUMBER>
        "student_name": (382, 662), # Paid By
        "syllabus": (150, 130),  # Syllabus
        "grade": (150, 160),  # Grade
        "total_amount": (400, 450),  # Grand Total
    }

    # 🔹 Step 4: Insert Static Text
    page.insert_text(text_positions["date"], payment.paymentDateNTime, fontsize=12, color=(0, 0, 0))
    page.insert_text(text_positions["invoice_number"], payment.invoice_number, fontsize=12, color=(0, 0, 0))
    page.insert_text(text_positions["student_name"], payment.student.studentName, fontsize=12, color=(0, 0, 0))
    page.insert_text(text_positions["syllabus"], payment.syllabus, fontsize=12, color=(0, 0, 0))
    page.insert_text(text_positions["grade"], str(payment.grade), fontsize=12, color=(0, 0, 0))
    page.insert_text(text_positions["total_amount"], f"₹ {payment.amount}", fontsize=12, color=(0, 0, 0))

    # 🔹 Step 5: Insert Subjects & Prices Dynamically
    subject_y_position = 250  # Start position for subjects
    price_x_position = 400  # Align price values

    subjects = []
    if payment.student.Physics:
        subjects.append(("Physics", 5000))
    if payment.student.Chemistry:
        subjects.append(("Chemistry", 4000))
    if payment.student.Biology:
        subjects.append(("Biology", 4500))
    if payment.student.Hindi:
        subjects.append(("Hindi", 3000))

    for subject, price in subjects:
        page.insert_text((150, subject_y_position), subject, fontsize=12, color=(0, 0, 0))
        page.insert_text((price_x_position, subject_y_position), f"₹ {price}", fontsize=12, color=(0, 0, 0))
        subject_y_position += 20  # Move down for next subject

    # 🔹 Step 6: Save the Updated PDF in Memory
    output_stream = io.BytesIO()
    doc.save(output_stream)
    doc.close()
    output_stream.seek(0)

    # 🔹 Step 7: Upload the Invoice to S3
    invoice_s3_key = f"invoices/{payment.invoice_number}.pdf"
    s3.upload_fileobj(output_stream, settings.AWS_STORAGE_BUCKET_NAME, invoice_s3_key, ExtraArgs={'ContentType': 'application/pdf'})

    # 🔹 Step 8: Return Invoice URL
    invoice_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{invoice_s3_key}"
    return invoice_url


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
    logger.debug("Entering paymenthandler view.")

    s = CustomUser.objects.get(studentName=request.session.get('studentN'))
    logger.debug(f"Retrieved student: {s.studentName}")

    a = Payment(
        student=s, syllabus=s.syllabus, grade=s.grade,
        amount=request.session.get('amountN', 0), paymentStatus=False,
        paymentDateNTime="0"
    )
    a.save()
    logger.debug("Payment object created but not finalized.")

    if request.method == "POST":
        try:
            # Extract payment details
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            logger.debug(f"Received payment details: {payment_id}, {razorpay_order_id}, {signature}")

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the signature
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            logger.debug(f"Signature verification result: {result}")

            if result:
                amount = request.session.get('amountN', 0) / 100
                try:
                    # Update payment details
                    a.amount = amount
                    a.paymentStatus = True
                    now = datetime.now()
                    a.paymentDateNTime = now.strftime("%Y-%m-%d %H:%M:%S")
                    a.save()
                    logger.debug("Payment successfully updated in database.")

                    # Generate invoice
                    invoice_path = generate_invoice_pdf(a)
                    logger.debug(f"Invoice generated: {invoice_path}")

                    # Render success page
                    context = {'status': True, 'invoice_url': invoice_path}
                    return render(request, 'status.html', context)
                except Exception as e:
                    logger.error(f"Error updating payment: {e}")
                    context = {'status': False}
                    return render(request, 'status.html', context)
            else:
                logger.warning("Signature verification failed.")
                context = {'status': False}
                return render(request, 'fail.html', context)
        except Exception as e:
            logger.error(f"Exception encountered: {e}")
            return HttpResponseBadRequest()
    else:
        logger.warning("Non-POST request made to paymenthandler.")
        return HttpResponseBadRequest()