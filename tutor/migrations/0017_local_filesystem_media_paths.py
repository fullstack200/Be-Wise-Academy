from urllib.parse import unquote, urlsplit

from django.core.files.storage import default_storage
from django.db import migrations, models


def normalize_media_paths(apps, schema_editor):
    media_models = (
        ("Resources", "document"),
        ("Quiz", "questionImage"),
        ("Blogs", "blogImage"),
    )
    for model_name, field_name in media_models:
        model = apps.get_model("tutor", model_name)
        for instance in (
            model.objects.exclude(**{f"{field_name}__isnull": True})
            .exclude(**{field_name: ""})
            .iterator()
        ):
            old_name = getattr(instance, field_name).name
            if not old_name.startswith("media/"):
                continue

            new_name = old_name[len("media/"):]
            if default_storage.exists(old_name):
                with default_storage.open(old_name, "rb") as source:
                    new_name = default_storage.save(new_name, source)
                default_storage.delete(old_name)

            setattr(instance, field_name, new_name)
            instance.save(update_fields=[field_name])

    payment_model = apps.get_model("payment", "Payment")
    for payment in payment_model.objects.exclude(invoice_url__isnull=True).exclude(invoice_url="").iterator():
        parsed_url = urlsplit(payment.invoice_url)
        invoice_path = unquote(parsed_url.path).lstrip("/")
        if not invoice_path.startswith("invoices/"):
            continue

        payment.invoice_url = default_storage.url(invoice_path)
        payment.save(update_fields=["invoice_url"])


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0007_payment_invoice_number_payment_invoice_url"),
        ("tutor", "0016_alter_quiz_questionimage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resources",
            name="document",
            field=models.FileField(upload_to="docs/"),
        ),
        migrations.AlterField(
            model_name="quiz",
            name="questionImage",
            field=models.ImageField(blank=True, null=True, upload_to="quiz/"),
        ),
        migrations.AlterField(
            model_name="blogs",
            name="blogImage",
            field=models.ImageField(
                height_field=None,
                max_length=1000,
                upload_to="blogs/",
                width_field=None,
            ),
        ),
        migrations.RunPython(normalize_media_paths, migrations.RunPython.noop),
    ]
