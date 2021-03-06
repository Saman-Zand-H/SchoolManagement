# Generated by Django 3.2.7 on 2021-10-29 11:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0025_auto_20211026_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='support',
            field=models.OneToOneField(blank=True, limit_choices_to={'user_type': 'SS'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_support', to=settings.AUTH_USER_MODEL),
        ),
    ]
