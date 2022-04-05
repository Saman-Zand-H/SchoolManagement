# Generated by Django 3.2.7 on 2022-03-22 15:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teachers', '0003_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='user',
            field=models.OneToOneField(limit_choices_to={'user_type': 'T'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]