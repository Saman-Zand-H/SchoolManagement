from celery import shared_task
from celery.utils.log import get_task_logger
from webpush import send_user_notification
from django.contrib.auth import get_user_model


logger = get_task_logger(__name__)


@shared_task(name="send_notification")
def send_notification_task(username, payload, ttl):
    """Sends notification to the user."""
    logger.info(
        f"""
            Task created for notification:
            username: {username}
            payload: {payload}
            ttl: {ttl}
        """)
    user = get_user_model().objects.get(username=username)
    return send_user_notification(user, 
                                  payload, 
                                  ttl)
    