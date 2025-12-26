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


from agents import gen_trace_id

async def get_questions(query: str, state):
    """Get clarifying questions for the query"""
    if not query or not query.strip():
        yield "Please enter a research query first.", state
        return
    
    trace_id = gen_trace_id()
    manager = ResearchManager()
    try:
        questions_data = await manager.get_clarifying_questions(query, trace_id=trace_id)
        questions_markdown = f"## Clarifying Questions\n\n"
        for i, q in enumerate(questions_data.questions, 1):
            questions_markdown += f"{i}. {q.question}\n\n"
        questions_markdown += "Please answer these questions to help refine your research query."
        yield questions_markdown, trace_id
    except Exception as e:
        yield f"Error generating questions: {str(e)}", state


async def run(query: str, send_email: bool, recipient_email: str, answer1: str, answer2: str, answer3: str, state):
    """Run research with optional clarification answers"""
    answers = [answer1, answer2, answer3] if (answer1 or answer2 or answer3) else None
    trace_id = state if state else None
    async for chunk in ResearchManager().run(query, send_email, recipient_email if recipient_email else None, answers, trace_id=trace_id):
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
    
    with gr.Row():
        get_questions_button = gr.Button("Get Clarifying Questions", variant="secondary")
        run_button = gr.Button("Run Research", variant="primary")
    
    questions_display = gr.Markdown(label="Clarifying Questions", visible=False)
    trace_state = gr.State(value=None)
    
    with gr.Group(visible=False) as clarification_group:
        gr.Markdown("### Answer these questions to refine your research (optional)")
        answer1_textbox = gr.Textbox(label="Question 1", lines=2)
        answer2_textbox = gr.Textbox(label="Question 2", lines=2)
        answer3_textbox = gr.Textbox(label="Question 3", lines=2)
    
    send_email_checkbox = gr.Checkbox(label="Send report via email", value=False)
    recipient_email_textbox = gr.Textbox(
        label="Your email address",
        visible=False,
        placeholder="Enter your email address"
    )
    report = gr.Markdown(label="Report")
    
    def handle_checkbox_change(send_email, recipient_email):
        """Update email field visibility and button state"""
        email_update = gr.update(visible=send_email)
        button_update = update_button_state(send_email, recipient_email)
        return email_update, button_update
    
    def handle_email_change(send_email, recipient_email):
        """Update button state based on checkbox and email"""
        return update_button_state(send_email, recipient_email)
    
    def show_questions(questions_output):
        """Show questions and answer fields"""
        if questions_output and "Clarifying Questions" in questions_output:
            return [
                gr.update(visible=True),
                gr.update(visible=True),
            ]
        return [
            gr.update(visible=False),
            gr.update(visible=False),
        ]
    
    get_questions_button.click(
        fn=get_questions,
        inputs=[query_textbox, trace_state],
        outputs=[questions_display, trace_state]
    ).then(
        fn=show_questions,
        inputs=questions_display,
        outputs=[questions_display, clarification_group]
    )
    
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
        inputs=[query_textbox, send_email_checkbox, recipient_email_textbox, answer1_textbox, answer2_textbox, answer3_textbox, trace_state],
        outputs=report
    )
    query_textbox.submit(
        fn=run,
        inputs=[query_textbox, send_email_checkbox, recipient_email_textbox, answer1_textbox, answer2_textbox, answer3_textbox, trace_state],
        outputs=report
    )

ui.launch(inbrowser=True)
