from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = """You are a quality evaluator for research reports. Your job is to assess whether a research report adequately addresses the original query.

Evaluate the report on:
1. Completeness - Does it fully answer the original query?
2. Quality - Is the information accurate, well-structured, and comprehensive?
3. Gaps - What aspects of the query are missing or insufficiently covered?
4. Search needs - Would additional searches improve the report?

Be thorough but fair. If the report is high quality and complete, indicate that. If there are gaps, be specific about what's missing and suggest what additional searches might help."""


class EvaluationResult(BaseModel):
    quality_score: float = Field(
        description="Quality score from 0.0 to 1.0, where 1.0 is excellent and complete",
        ge=0.0,
        le=1.0
    )
    is_complete: bool = Field(
        description="Whether the report fully addresses the original query"
    )
    missing_aspects: list[str] = Field(
        description="List of aspects or topics that are missing or insufficiently covered in the report"
    )
    needs_more_searches: bool = Field(
        description="Whether additional searches would improve the report quality"
    )
    suggested_searches: list[str] = Field(
        description="List of suggested search terms if needs_more_searches is True, empty list otherwise"
    )
    feedback: str = Field(
        description="Detailed feedback about the report quality, completeness, and recommendations"
    )


evaluator_agent = Agent(
    name="EvaluatorAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=EvaluationResult,
)

