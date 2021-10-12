from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Class, Teacher


@receiver(post_save, sender=Class)
def update_teacher_classes(sender, instance, **kwargs):
    if instance.teachers:
        teachers = instance.teachers.all()
        for teacher in teachers:
            teacher.classes.add(instance)