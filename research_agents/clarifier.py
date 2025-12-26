from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = """You are a helpful research assistant that asks clarifying questions to better understand research queries.
Given an initial research query, generate exactly 3 clarifying questions that will help refine and focus the research.
The questions should:
- Help understand the user's specific interests or goals
- Clarify ambiguous aspects of the query
- Identify the scope or depth of information needed
- Be concise and easy to answer

Output exactly 3 questions that will improve the quality and relevance of the research."""


class ClarifyingQuestion(BaseModel):
    question: str = Field(description="A clarifying question to better understand the research query")


class ClarifyingQuestions(BaseModel):
    questions: list[ClarifyingQuestion] = Field(
        description="A list of exactly 3 clarifying questions",
        min_length=3,
        max_length=3
    )


clarifier_agent = Agent(
    name="ClarifierAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarifyingQuestions,
)

