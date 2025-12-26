import gradio as gr
import re
from dotenv import load_dotenv
from research_agents.manager import ResearchManager

load_dotenv(override=True)


def is_valid_email(email: str) -> bool:
    """Validate email format using a basic regex pattern"""
    if not email or not email.strip():
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


async def run(query: str, send_email: bool, recipient_email: str):
    async for chunk in ResearchManager().run(query, send_email, recipient_email if recipient_email else None):
        yield chunk


def update_button_state(send_email: bool, recipient_email: str):
    """Enable button only if email is not required or valid email is provided"""
    if send_email:
        if not recipient_email or not recipient_email.strip():
            return gr.update(interactive=False)
        if not is_valid_email(recipient_email):
            return gr.update(interactive=False)
    return gr.update(interactive=True)


with gr.Blocks(theme=gr.themes.Monochrome()) as ui:
    gr.Markdown("# Research Helper")
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    send_email_checkbox = gr.Checkbox(label="Send report via email", value=False)
    recipient_email_textbox = gr.Textbox(
        label="Your email address",
        visible=False,
        placeholder="Enter your email address"
    )
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")
    
    def handle_checkbox_change(send_email, recipient_email):
        """Update email field visibility and button state"""
        email_update = gr.update(visible=send_email)
        button_update = update_button_state(send_email, recipient_email)
        return email_update, button_update
    
    def handle_email_change(send_email, recipient_email):
        """Update button state based on checkbox and email"""
        return update_button_state(send_email, recipient_email)
    
    send_email_checkbox.change(
        fn=handle_checkbox_change,
        inputs=[send_email_checkbox, recipient_email_textbox],
        outputs=[recipient_email_textbox, run_button]
    )
    
    recipient_email_textbox.change(
        fn=handle_email_change,
        inputs=[send_email_checkbox, recipient_email_textbox],
        outputs=run_button
    )
    
    run_button.click(
        fn=run,
        inputs=[query_textbox, send_email_checkbox, recipient_email_textbox],
        outputs=report
    )
    query_textbox.submit(
        fn=run,
        inputs=[query_textbox, send_email_checkbox, recipient_email_textbox],
        outputs=report
    )

ui.launch(inbrowser=True)
