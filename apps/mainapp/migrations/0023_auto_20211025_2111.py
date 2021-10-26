# Generated by Django 3.2.7 on 2021-10-25 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0022_auto_20211022_2021'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='school',
            options={'permissions': (('support', "has support staff's permissions"),)},
        ),
        migrations.AlterField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_school', to='mainapp.school'),
        ),
    ]
