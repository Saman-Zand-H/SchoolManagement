# Generated by Django 3.2.7 on 2022-04-02 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supports', '0004_alter_school_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='school',
            options={'permissions': (('support', "has support staff's permissions"),)},
        ),
    ]