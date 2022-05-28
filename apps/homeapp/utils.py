from django.core.mail import mail_admins
from django.template.loader import render_to_string



def send_email_to_support(name:str, email:str, message:str):
    """
    Sends mail to the admins defined in the settings. 
    """
    template = "home/email/support_email.html"
    context = {
        "name": name,
        "email": email,
        "message": message,
    }
    html_content = render_to_string(template, context)
    mail_admins("Support message", 
                html_message=html_content, 
                fail_silently=False,
                message=f"{message} by {name}: {email}")
