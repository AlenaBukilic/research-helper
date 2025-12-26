import os
from typing import Dict

import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
from agents import Agent, function_tool


@function_tool
def send_email(subject: str, html_body: str, recipient_email: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body to the recipient_email address."""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email(os.environ.get("EMAIL_FROM"))
    
    if not recipient_email or not recipient_email.strip():
        return {"error": "recipient_email is required"}
    
    to_email = To(recipient_email.strip())
    content = Content("text/html", html_body)
    
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print("Email response", response.status_code)
    return "success"


INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line.
If the input contains a line like "Recipient email: [email address]", extract that email address 
and pass it as the recipient_email parameter to the send_email function. The recipient_email parameter is required."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
