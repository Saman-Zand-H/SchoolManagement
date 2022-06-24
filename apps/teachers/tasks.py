from celery import shared_task
from celery.utils.log import get_task_logger

from mainapp.models import Exam, Subject, Class
from teachers.models import Teacher


logger = get_task_logger(__name__)


@shared_task(name="create_exam")
def create_exam_task(subject, 
                     exam_class, 
                     full_score, 
                     timestamp, 
                     teacher, 
                     visible_to_students):
    logger.info(f"""
                 Creating exam: 
                    subject:{subject}
                    class_exam: {exam_class}
                    full_score: {full_score}
                    timestamp: {timestamp}
                    teacher: {teacher}
                    visible_to_students: {visible_to_students}
    """)
    exam_class_instance = Class.objects.get(pk=exam_class)
    teacher_instance = Teacher.objects.get(pk=teacher)
    return Exam.objects.create(subject=subject,
                               exam_class=exam_class_instance,
                               full_score=full_score,
                               timestamp=timestamp,
                               teacher=teacher_instance,
                               visible_to_students=visible_to_students)
