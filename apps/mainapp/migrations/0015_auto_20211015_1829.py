# Generated by Django 3.2.7 on 2021-10-15 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0014_auto_20211014_0757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='teachers',
            field=models.ManyToManyField(blank=True, related_name='class_teachers', to='mainapp.Teacher'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_teacher', to='mainapp.teacher'),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('support', models.ForeignKey(blank=True, limit_choices_to={'user_type': 'SS'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='school_support', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
