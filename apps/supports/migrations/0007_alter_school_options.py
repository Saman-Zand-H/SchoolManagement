# Generated by Django 3.2.7 on 2022-06-20 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supports', '0006_alter_school_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='school',
            options={'permissions': (('support', "has support staff's permissions"), ('api_post', 'has permission to send a post_request to api'))},
        ),
    ]
