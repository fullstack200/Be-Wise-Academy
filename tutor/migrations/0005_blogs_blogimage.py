# Generated by Django 4.2.9 on 2024-01-05 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0004_blogs'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogs',
            name='blogImage',
            field=models.ImageField(default=0, max_length=1000, upload_to='upload/'),
            preserve_default=False,
        ),
    ]