# Generated by Django 3.2.7 on 2021-11-08 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_customuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phonenumber_verification_code',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
    ]
