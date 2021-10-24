# Generated by Django 3.2.7 on 2021-10-15 19:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0015_auto_20211015_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='school',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='class_school', to='mainapp.school'),
        ),
        migrations.AlterField(
            model_name='class',
            name='class_id',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='class',
            name='subjects',
            field=models.ManyToManyField(related_name='class_subjects', to='mainapp.Subject'),
        ),
        migrations.AlterField(
            model_name='class',
            name='teachers',
            field=models.ManyToManyField(related_name='class_teachers', to='mainapp.Teacher'),
        ),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subject',
            name='teachers',
            field=models.ManyToManyField(related_name='subject_teacher', to='mainapp.Teacher'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='degree',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='university',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('school', 'class_id')},
        ),
    ]
