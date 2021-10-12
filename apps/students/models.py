# from django.db import models
# from django.contrib.auth import get_user_model

# from mainapp.models import Class


# class Student(models.Model):
#     user = models.OneToOneField(
#         get_user_model(),
#         on_delete=models.CASCADE,
#     )
#     student_class = models.ForeignKey(
#         Class,
#         on_delete=models.CASCADE,
#         related_name="students",
#     )

#     def __str__(self):
#         return self.user.user_id
