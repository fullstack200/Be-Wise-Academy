def generate_invoice_pdf(payment):
    from .views import generate_invoice_pdf as generate_local_invoice

    return generate_local_invoice(payment)
