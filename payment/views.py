from django.shortcuts import render
from datetime import datetime
from tutor.models import Fee,Syllabus
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .models import Payment
from users.models import CustomUser
from django.contrib.auth.decorators import login_required
import calendar
import fitz
import logging
import io

logger = logging.getLogger(__name__)

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
	auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@login_required
def payment_invoice_page(request):
    user = request.user  
    currency = 'INR'
    tot_amt = 0

    # Calculate total amount based on enrolled subjects
    subjects = ["Physics", "Chemistry", "Biology", "Hindi"]
    for subject in subjects:
        if getattr(user, subject, False):  # Check if user is enrolled in subject
            syllabus_obj = Syllabus.objects.get(syllabusName=user.syllabus)
            fee_obj = Fee.objects.get(syllabus=syllabus_obj, subject=subject, gradeNumber=user.grade)
            tot_amt += fee_obj.fee

    amount = tot_amt * 100  # Convert to smallest currency unit
    request.session['studentN'] = user.studentName
    request.session['amountN'] = amount

    razorpay_order = None
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': currency,
            'payment_capture': '0'
        })
        razorpay_order_id = razorpay_order['id']
    except Exception as e:
        logger.error(f"Razorpay error: {e}")
        razorpay_order_id = None 
        
    # Order ID of the newly created order
    razorpay_order_id = razorpay_order['id'] if razorpay_order else None
    callback_url = 'paymenthandler/'

    # Fetch invoices
    payments = Payment.objects.filter(student=user, invoice_url__isnull=False).order_by('-paymentDateNTime')[:4]

    invoices_by_year = {}

    for payment in payments:
        invoice_url = payment.invoice_url
        if invoice_url:
            try:
                filename = invoice_url.split('/')[-1]  # Extract filename
                date_part = filename.replace('invoice', '')[:8]  # Extract YYYYDDMM
                year,month_number,day = int(date_part[:4]), int(date_part[4:6]), int(date_part[6:])
                month_name = calendar.month_name[month_number]
                month_year_key = f"{month_name} {year}"

                if year not in invoices_by_year:
                    invoices_by_year[year] = {}

                if month_year_key not in invoices_by_year[year]:
                    invoices_by_year[year][month_year_key] = []

                invoices_by_year[year][month_year_key].append({
                    'day': day,
                    'month': month_name,
                    'year': year,
                    'url': invoice_url
                })

            except Exception as e:
                logger.error(f"Error parsing invoice: {e}")

    # Context for rendering the template
    context = {
        'user': user,
        'amount': tot_amt,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url,
        'invoices_by_year': invoices_by_year
    }

    return render(request, 'payment.html', context)

def generate_invoice_pdf(payment):
    """Generate an invoice PDF and save it to the configured file storage."""
    template_path = finders.find('invoice_template.pdf')
    font_path = finders.find('fonts/Montserrat-Regular.ttf')
    if not template_path:
        raise FileNotFoundError("Static invoice template was not found.")
    if not font_path:
        raise FileNotFoundError("Static invoice font was not found.")

    with open(template_path, 'rb') as template_file:
        template_bytes = template_file.read()
    if not template_bytes.strip():
        raise ValueError("Invoice template file is empty or corrupted.")
    if not template_bytes.startswith(b'%PDF'):
        raise ValueError("Invoice template data is invalid or corrupted.")

    with open(font_path, 'rb') as font_file:
        font_bytes = font_file.read()
    if not font_bytes.strip():
        raise ValueError("Invoice font file is empty or corrupted.")

    doc = fitz.open(stream=template_bytes, filetype="pdf")
    page = doc[0]

    font_name="montserrat"
    page.insert_font(fontname=font_name, fontbuffer=font_bytes)

    text_positions = {
    "date": (167.40, 188.64),
    "invoice_number": (161.43, 226.54),
    "student_name": (382.24, 188.64),
    "total_amount": (465.03, 600.97),  # Moved up by 0.1 cm and aligned with price_x
    }

    # 🔹 Step 7: Insert Static Text with Montserrat Font
    current_date = datetime.now().strftime("%d-%m-%Y")  
    page.insert_text(text_positions["date"], current_date, fontsize=12, fontname=font_name, color=(0, 0, 0))
    page.insert_text(text_positions["invoice_number"], payment.invoice_number, fontsize=12, fontname=font_name, color=(0, 0, 0))
    page.insert_text(text_positions["student_name"], payment.student.studentName, fontsize=12, fontname=font_name, color=(0, 0, 0))
    page.insert_text(text_positions["total_amount"], f"₹ {str(payment.amount)}", fontsize=12, fontname=font_name, color=(0, 0, 0))
    
    # 🔹 Step 8: Extract Subjects & Prices Dynamically
    subject_x = 118.48  # X position for subjects (from SUBJECT 1)
    price_x = 467.03  # X position for prices (from PRICE)
    start_y = 374.39  # Y position for first subject (from SUBJECT 1)
    row_spacing = 28.35  # 1 cm gap between rows

    subjects = []

    subject_mapping = {
        "Physics": payment.student.Physics,
        "Chemistry": payment.student.Chemistry,
        "Biology": payment.student.Biology,
        "Hindi": payment.student.Hindi,
    }

    for subject_name, is_selected in subject_mapping.items():
        if is_selected:
            syllabus_obj = Syllabus.objects.get(syllabusName=payment.student.syllabus)
            fee_obj = Fee.objects.get(syllabus=syllabus_obj, subject=subject_name, gradeNumber=payment.student.grade)
            subjects.append((subject_name, fee_obj.fee))

    # 🔹 Step 9: Insert Subjects & Prices
    for index, (subject, price) in enumerate(subjects):
        y_position = start_y + (index * row_spacing)  # Shift down for each subject

        # Insert Subject & Price in the same row
        page.insert_text((subject_x, y_position), subject, fontsize=12, fontname=font_name, color=(0, 0, 0))
        page.insert_text((price_x, y_position), f"₹ {price}", fontsize=12, fontname=font_name, color=(0, 0, 0))

    # Save the updated PDF in memory before writing it through Django storage.
    output_stream = io.BytesIO()
    doc.save(output_stream)
    doc.close()
    output_stream.seek(0)

    invoice_name = default_storage.save(
        f"invoices/{payment.invoice_number}.pdf",
        ContentFile(output_stream.getvalue()),
    )
    invoice_url = default_storage.url(invoice_name)
    payment.invoice_url = invoice_url
    payment.save(update_fields=['invoice_url'])
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
        paymentDateNTime="0", invoice_url=""
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
                    a.invoice_url = invoice_path
                    a.save()
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