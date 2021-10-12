# Generated by Django 3.2.7 on 2021-09-30 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('S', 'student'), ('T', 'teacher'), ('IT', 'IT staff'), ('P', 'principal'), ('O', 'others')], max_length=3, null=True),
        ),
    ]
