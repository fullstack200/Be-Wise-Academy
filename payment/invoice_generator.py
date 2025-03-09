import boto3
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def generate_invoice_pdf(payment):
    s3_client = boto3.client('s3')
    
    # Mock PDF download
    invoice_pdf = io.BytesIO()
    s3_client.download_fileobj('nbewise', 'static/invoice_template.pdf', invoice_pdf)
    invoice_pdf.seek(0)
    if not invoice_pdf.getvalue().strip():
        raise ValueError("Downloaded PDF file is empty or corrupted.")
    if not invoice_pdf.getvalue().startswith(b"%PDF"):
        raise ValueError("Downloaded PDF data is invalid or corrupted.")

    # Mock Font download
    montserrat_font = io.BytesIO()
    s3_client.download_fileobj('nbewise', 'static/fonts/Montserrat-Regular.ttf', montserrat_font)
    montserrat_font.seek(0)
    if not montserrat_font.getvalue().strip():
        raise ValueError("Downloaded font file is empty or corrupted.")

    # Generate invoice PDF
    output_pdf = io.BytesIO()
    c = canvas.Canvas(output_pdf, pagesize=A4)
    c.drawString(100, 750, f"Invoice Number: {payment.invoice_number}")
    c.drawString(100, 730, f"Student Name: {payment.student.studentName}")
    c.drawString(100, 710, f"Syllabus: {payment.student.syllabus}")
    c.drawString(100, 690, f"Grade: {payment.student.grade}")
    c.drawString(100, 670, f"Amount: ${payment.amount}")
    c.showPage()
    c.save()

    # Upload PDF to S3
    output_pdf.seek(0)
    invoice_key = f"invoices/{payment.invoice_number}.pdf"
    s3_client.upload_fileobj(output_pdf, 'nbewise', invoice_key)

    # Generate Invoice URL
    invoice_url = f"https://nbewise.s3.amazonaws.com/{invoice_key}"
    payment.invoice_url = invoice_url
    return invoice_url
