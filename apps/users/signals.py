from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group


from mainapp.models import Student, Teacher


@receiver(post_save, sender='users.CustomUser')
def get_user_typed(sender, instance, **kwargs):
    if not instance.is_superuser:
        if instance.user_type == "S":
            Student.objects.create(user=instance)
        elif instance.user_type == "T":
            Teacher.objects.create(user=instance)
        else:
            # TODO: Consider different staffs
            pass