# Generated by Django 4.2.8 on 2024-02-04 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0007_mathquizresult_q10_mathquizresult_q9_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mathquizresult',
            name='quizTime',
            field=models.DateField(default=0),
        ),
        migrations.AlterField(
            model_name='sciencequizresult',
            name='quizTime',
            field=models.DateField(default=0),
        ),
    ]
