# Generated by Django 3.2.7 on 2021-12-22 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0033_article'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='subject',
        ),
        migrations.AddField(
            model_name='article',
            name='subjects',
            field=models.ManyToManyField(related_name='article_subjects', to='mainapp.Subject'),
        ),
        migrations.AddField(
            model_name='article',
            name='title',
            field=models.CharField(default='Title', max_length=80),
            preserve_default=False,
        ),
    ]
