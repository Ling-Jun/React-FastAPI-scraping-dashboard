from fastapi import APIRouter
from utils.email_handling import sendEmail
from utils.config import Grant

send2custom_email = APIRouter()


@send2custom_email.post("/send_email")
async def send_to_custom_email(data: Grant):

    sendEmail(
        email_content=f"""
        <html>
        <head></head>
        <body>
            <h1 style="color:blue;">Action Required!</h1>
            <p style="font-size:16px; color:grey;">
            You are requested to review the changes at URL: {data.url},
            with status: {data.status}!
            </p>
        </body>
        </html>
        """,
        recipients=data.recipient,
        email_subject="This change has a status: " + data.status,
    )
    return "Email sent"
