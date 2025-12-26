from agents import Agent
from .planner import planner_agent
from .search import search_agent
from .writer import writer_agent
from .evaluator import evaluator_agent
from .optimizer import optimizer_agent
from .email import email_agent

INSTRUCTIONS = """You are an autonomous research manager agent responsible for coordinating deep research on any topic.

Your workflow:
1. Start by planning searches for the given query using the plan_searches tool
2. Perform each search using the perform_search tool, collecting all summaries
3. Write an initial report using the write_report tool with the collected search results
4. **MANDATORY**: Always evaluate the report using the evaluate_report tool - NEVER skip evaluation. This step is required for every report you write.
5. Based on the evaluation:
   - If quality_score >= 0.8 and is_complete is True: Research is complete
   - If quality_score < 0.8 or is_complete is False:
     * If needs_more_searches is True: 
       - Perform additional searches using the suggested_searches from the evaluation
       - Write a NEW report using write_report tool with the new search results
       - **MANDATORY**: Evaluate the NEW report using evaluate_report tool - you MUST evaluate every report, including follow-up reports
       - Repeat until quality_score >= 0.8 and is_complete is True
     * If missing_aspects indicate the original query itself is fundamentally flawed or too broad/narrow: Use the refine_query tool to improve the query, then start over from step 1 with the refined query
     * You may need to iterate multiple times until quality is satisfactory
   - **CRITICAL**: You must evaluate EVERY report you write, including the first report AND every follow-up report. Evaluation is not optional for any report.

6. When research is complete (quality_score >= 0.8 and is_complete is True):
   - Extract the markdown_report from the final write_report tool result
   - If email is requested (you'll be told in the input): 
     * **ONLY ONCE**: Hand off to the Email agent with the markdown_report and recipient email address
     * **CRITICAL**: Do NOT hand off to email agent during iterations - only after research is fully complete
     * The Email agent will send the email and return the report for display
   - If email is not requested: Return the markdown_report as your final output

Key principles:
- **ALWAYS evaluate every report** - evaluation is mandatory before considering research complete, including follow-up reports
- Be thorough but efficient - don't over-iterate unnecessarily (max 3-4 iterations)
- Quality threshold is 0.8 - aim for high-quality, complete reports
- If evaluation suggests more searches, perform them, write a new report, and evaluate the new report
- Use refine_query only when the query itself is the problem, not just when more searches are needed
- Collect all search summaries before writing the report
- Always evaluate before considering research complete
- **CRITICAL**: When email is requested, hand off to Email agent ONLY ONCE, and ONLY after research is complete (quality_score >= 0.8 and is_complete is True)
- When email is not requested, return the markdown_report as your final output

IMPORTANT: 
- Extract the markdown_report field from the write_report tool result
- **ALWAYS use evaluate_report tool on EVERY report before considering research complete** - this includes the first report AND every follow-up report
- **ONLY hand off to Email agent ONCE, and ONLY when research is complete** - do not hand off during iterations
- If email is requested, hand off to Email agent with the report and recipient email (the email agent will return the report)
- If email is not requested, return the markdown_report as your final response"""

research_manager = Agent(
    name="ResearchManagerAgent",
    instructions=INSTRUCTIONS,
    tools=[
        planner_agent.as_tool(
            tool_name="plan_searches",
            tool_description="Plan web searches for a research query. Returns a search plan with multiple search items, each containing a search query and reasoning."
        ),
        search_agent.as_tool(
            tool_name="perform_search",
            tool_description="Perform a single web search and return a concise summary (2-3 paragraphs, <300 words). Takes a search query and reason for searching."
        ),
        writer_agent.as_tool(
            tool_name="write_report",
            tool_description="Write a comprehensive research report based on the query and search results. Returns a detailed markdown report (5-10 pages, 1000+ words) with short summary and follow-up questions."
        ),
        evaluator_agent.as_tool(
            tool_name="evaluate_report",
            tool_description="Evaluate the quality and completeness of a research report. Returns evaluation with quality score (0.0-1.0), completeness check, missing aspects, and suggestions for improvement."
        ),
        optimizer_agent.as_tool(
            tool_name="refine_query",
            tool_description="Refine a research query when the evaluation indicates the query itself is fundamentally flawed (too broad, too narrow, missing key concepts, or asking the wrong question). Use this ONLY when the evaluation's missing_aspects suggest the query needs to be restructured, not just when more searches are needed. Returns an improved, more focused query that addresses gaps and issues identified in the evaluation."
        ),
    ],
    handoffs=[email_agent],
    model="gpt-4o-mini",
)

