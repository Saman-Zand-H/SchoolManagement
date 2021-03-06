# Generated by Django 3.2.7 on 2021-11-02 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0003_teacher'),
        ('supports', '0003_school'),
        ('mainapp', '0028_auto_20211102_1758'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='school',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='user',
        ),
        migrations.AlterField(
            model_name='class',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_school', to='supports.school'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_teacher', to='teachers.teacher'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_teacher', to='teachers.teacher'),
        ),
        migrations.DeleteModel(
            name='School',
        ),
        migrations.DeleteModel(
            name='Teacher',
        ),
    ]
