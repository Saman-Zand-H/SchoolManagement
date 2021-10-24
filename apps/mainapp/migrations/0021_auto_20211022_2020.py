# Generated by Django 3.2.7 on 2021-10-22 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0020_alter_school_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='teachers',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='teachers',
        ),
        migrations.AddField(
            model_name='subject',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subject_teacher', to='mainapp.teacher'),
        ),
        migrations.AlterField(
            model_name='school',
            name='support',
            field=models.OneToOneField(blank=True, limit_choices_to={'user_type': 'SS'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='school_support', to=settings.AUTH_USER_MODEL),
        ),
    ]
