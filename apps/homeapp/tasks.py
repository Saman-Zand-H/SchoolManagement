from celery import shared_task
from celery.utils.log import get_task_logger

from .utils import send_email_to_support


logger = get_task_logger(__name__)


@shared_task(name="send_email_to_support")
def support_email_task(name:str, email:str, text:str):
    """Sends client's support message to the administrator."""
    logger.info("Sending support message to the administrator.")
    logger.info("Name: %s", name)
    logger.info("Email: %s", email)
    logger.info("Text: %s", text)
    return send_email_to_support(name, email, text)
