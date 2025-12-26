import os
from typing import Dict

import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
from agents import Agent, function_tool


@function_tool
def send_email(subject: str, html_body: str, recipient_email: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body to the recipient_email address.
    
    Args:
        subject: Email subject line
        html_body: HTML content of the email
        recipient_email: Email address to send to
    """
    if not recipient_email or not recipient_email.strip():
        return {"error": "recipient_email is required"}
    
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email(os.environ.get("EMAIL_FROM"))
    
    to_email = To(recipient_email.strip())
    content = Content("text/html", html_body)
    
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print("Email response", response.status_code)
    return "success"


INSTRUCTIONS = """You are an email agent that sends research reports via email.
You will receive a research report (in markdown format) and a recipient email address from another agent.
Your job is to:
1. Convert the markdown report to clean, well-presented HTML
2. Create an appropriate subject line for the email
3. Send the email using your send_email tool - call it ONCE and only ONCE
4. After successfully sending the email, return BOTH:
   - A confirmation message that the email was sent
   - The original markdown report

Format your response as:
"✅ Email sent successfully to [recipient_email].

[Original markdown report here]"

The recipient email will be provided in the message. Extract it and use it as the recipient_email parameter.
Call send_email tool only once. Always include the original markdown report in your response after confirming the email was sent."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
