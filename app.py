import gradio as gr
import re
from dotenv import load_dotenv
from agents import Runner, trace, gen_trace_id
from research_agents.clarifier import clarifier_agent, ClarifyingQuestions
from research_agents.research_manager import research_manager

load_dotenv(override=True)


def is_valid_email(email: str) -> bool:
    """Validate email format using a basic regex pattern"""
    if not email or not email.strip():
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def refine_query(original_query: str, answers: list[str] | None) -> str:
    """Refine the query by incorporating clarification answers"""
    if not answers or len(answers) == 0:
        return original_query
    
    answers_text = "\n".join([f"- {answer}" for answer in answers if answer and answer.strip()])
    if answers_text:
        return f"{original_query}\n\nAdditional context from clarification:\n{answers_text}"
    return original_query


async def get_questions(query: str, state):
    """Get clarifying questions for the query"""
    if not query or not query.strip():
        yield "Please enter a research query first.", state
        return
    
    trace_id = gen_trace_id()
    try:
        with trace("Clarification", trace_id=trace_id):
            result = await Runner.run(
                clarifier_agent,
                f"Research query: {query}",
            )
            questions_data = result.final_output_as(ClarifyingQuestions)
            questions_markdown = f"## Clarifying Questions\n\n"
            for i, q in enumerate(questions_data.questions, 1):
                questions_markdown += f"{i}. {q.question}\n\n"
            questions_markdown += "Please answer these questions to help refine your research query."
            yield questions_markdown, trace_id
    except Exception as e:
        yield f"Error generating questions: {str(e)}", state


async def run(query: str, send_email: bool, recipient_email: str, answer1: str, answer2: str, answer3: str, state):
    """Run autonomous research with optional clarification answers"""
    if not query or not query.strip():
        yield "Please enter a research query."
        return
    
    trace_id = state if state else gen_trace_id()
    
    answers = [answer1, answer2, answer3] if (answer1 or answer2 or answer3) else None
    refined_query = refine_query(query, answers)
    
    with trace("Research trace", trace_id=trace_id):
        print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
        print(f"Starting research... This may take a few minutes.")
        yield f"Starting research... This may take a few minutes."
        
        input_message = f"Research query: {refined_query}\n\nPlease conduct thorough research on this topic. Plan searches, perform them, write a report, evaluate it, and iterate if needed until you have a high-quality, complete report."
        
        if send_email:
            if not recipient_email or not recipient_email.strip():
                yield "Error: Email address is required when 'Send report via email' is checked."
                return
            if not is_valid_email(recipient_email):
                yield "Error: Please provide a valid email address."
                return
            input_message += f"\n\nIMPORTANT: After completing the research and ensuring the report is high quality, hand off to the Email agent to send the final report to {recipient_email}. Include the recipient email in your handoff message."
        
        try:
            result = await Runner.run(
                research_manager,
                input_message,
            )
            
            final_output = str(result.final_output)
            
            if "✅ Email sent successfully" in final_output:
                parts = final_output.split("✅ Email sent successfully")
                if len(parts) > 1:
                    report_part = parts[1].strip()
                    lines = report_part.split("\n")
                    if lines and ("to" in lines[0].lower() or "@" in lines[0]):
                        final_output = "\n".join(lines[1:]).strip()
                    else:
                        final_output = report_part
            else:
                final_output = final_output.strip()
            
            if final_output.startswith("```"):
                lines = final_output.split("\n")
                if lines[0].startswith("```"):
                    final_output = "\n".join(lines[1:])
                if final_output.endswith("```"):
                    final_output = final_output[:-3].strip()
            
            if not final_output or len(final_output) < 50:
                yield "Error: Report not found in output. Please check the trace link for details."
                return
            
            yield final_output
            
        except Exception as e:
            yield f"Error during research: {str(e)}"


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
