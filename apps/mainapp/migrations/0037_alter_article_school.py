# Generated by Django 3.2.7 on 2021-12-23 14:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supports', '0003_school'),
        ('mainapp', '0036_article_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_school', to='supports.school'),
        ),
    ]