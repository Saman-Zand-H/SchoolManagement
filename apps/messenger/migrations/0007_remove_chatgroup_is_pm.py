# Generated by Django 3.2.7 on 2022-03-25 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0006_alter_memeber_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatgroup',
            name='is_pm',
        ),
    ]
