# Generated by Django 3.2.7 on 2021-10-01 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0009_alter_exam_examed_class'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exam',
            old_name='examed_class',
            new_name='tested_class',
        ),
        migrations.AlterField(
            model_name='exam',
            name='timestamp',
            field=models.DateField(),
        ),
    ]
