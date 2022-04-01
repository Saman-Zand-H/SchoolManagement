# Generated by Django 3.2.7 on 2022-03-26 12:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0013_alter_chatgroup_group_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='id',
        ),
        migrations.AddField(
            model_name='message',
            name='message_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
