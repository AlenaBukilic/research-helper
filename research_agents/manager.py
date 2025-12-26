from agents import Runner, trace, gen_trace_id
from .search import search_agent
from .planner import planner_agent, WebSearchItem, WebSearchPlan
from .writer import writer_agent, ReportData
from .email import email_agent
from .clarifier import clarifier_agent, ClarifyingQuestions
import asyncio

class ResearchManager:

    async def run(self, query: str, send_email: bool = False, recipient_email: str | None = None, clarification_answers: list[str] | None = None):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            
            # Refine query with clarification answers if provided
            refined_query = self.refine_query(query, clarification_answers)
            
            print("Starting research...")
            search_plan = await self.plan_searches(refined_query)
            yield "Searches planned, starting to search..."     
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(refined_query, search_results)
            if send_email:
                if not recipient_email or not recipient_email.strip():
                    yield "Error: Email address is required when 'Send report via email' is checked."
                    yield report.markdown_report
                    return
                yield "Report written, sending email..."
                await self.send_email(report, recipient_email)
                yield "Email sent, research complete"
            else:
                yield "Report complete"
            yield report.markdown_report
    
    async def get_clarifying_questions(self, query: str) -> ClarifyingQuestions:
        """Generate clarifying questions for the research query"""
        print("Generating clarifying questions...")
        result = await Runner.run(
            clarifier_agent,
            f"Research query: {query}",
        )
        return result.final_output_as(ClarifyingQuestions)
    
    def refine_query(self, original_query: str, answers: list[str] | None) -> str:
        """Refine the query by incorporating clarification answers"""
        if not answers or len(answers) == 0:
            return original_query
        
        # Combine original query with answers
        answers_text = "\n".join([f"- {answer}" for answer in answers if answer and answer.strip()])
        if answers_text:
            return f"{original_query}\n\nAdditional context from clarification:\n{answers_text}"
        return original_query
        

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query """
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData, recipient_email: str | None = None) -> None:
        print("Writing email...")
        input_message = report.markdown_report
        input_message += f"\n\nRecipient email: {recipient_email}"
        await Runner.run(
            email_agent,
            input_message,
        )
        print("Email sent")
        return report