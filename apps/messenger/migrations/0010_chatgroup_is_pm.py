# Generated by Django 3.2.7 on 2022-03-25 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0009_delete_savedmessages'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='is_pm',
            field=models.BooleanField(default=True),
        ),
    ]
