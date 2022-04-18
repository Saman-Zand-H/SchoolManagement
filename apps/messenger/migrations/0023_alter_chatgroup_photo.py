# Generated by Django 3.2.7 on 2022-04-10 10:54

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0022_member_last_read_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='media', validators=[users.models.validate_file_size, users.models.validate_file_extension]),
        ),
    ]