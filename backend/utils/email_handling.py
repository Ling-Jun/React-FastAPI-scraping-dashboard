from email.message import EmailMessage
import smtplib
from utils.config import AutoEmail


def sendEmail(
    email_content: str, recipients: str, email_subject="Significant Changes Detected!"
):
    """
    We won't be able to connect to Gmail server if using VPN!!!!!!!
    """
    email_address = AutoEmail.BTAP_verification_host_email.value
    email_password = AutoEmail.BTAP_verification_host_email_password.value

    if isinstance(recipients, str):
        recipients = [recipients]
    msg = EmailMessage()
    msg["Subject"] = email_subject
    msg["From"] = email_address
    msg["To"] = ", ".join(recipients)
    msg.set_content(email_content, subtype="html")
    # send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)
