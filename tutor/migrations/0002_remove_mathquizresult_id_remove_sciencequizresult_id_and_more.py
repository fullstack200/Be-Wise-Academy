# Generated by Django 4.2.9 on 2024-01-05 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mathquizresult',
            name='id',
        ),
        migrations.RemoveField(
            model_name='sciencequizresult',
            name='id',
        ),
        migrations.AddField(
            model_name='mathquizresult',
            name='test_id',
            field=models.CharField(default=0, max_length=50, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sciencequizresult',
            name='test_id',
            field=models.CharField(default=0, max_length=50, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
