import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email(subject, body, to_email):
    sender = "Private person <from@example.com>"

    message = EmailMessage()
    message.set_content(body)
    message["subject"] = subject
    message["from"] = sender
    message["to"] = to_email       

    smtp_password = os.getenv("SMTP_PASSWORD")

    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.starttls()
        server.login("32215e01fc031f", smtp_password)
        server.send_message(message)
        return "Email sent successfully"

send_email("Test", "EmailAgent", "ein1crt@bolton.ac.uk")