# Generated by Django 3.2.7 on 2022-03-25 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0004_message_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='unread',
            field=models.BooleanField(default=False),
        ),
    ]
