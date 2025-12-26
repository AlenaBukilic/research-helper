# Research Helper

An AI-powered research assistant built with Gradio and OpenAI Agents that performs deep research on any topic. The system uses a multi-agent architecture to plan searches, gather information, synthesize comprehensive reports, and deliver them via email.

## Features

- **Multi-Agent Research Pipeline**: Orchestrates specialized AI agents for clarification, planning, searching, writing, and email delivery
- **Query Clarification** (optional): Generates 3 clarifying questions to refine and focus research queries before starting
- **Intelligent Search Planning**: Automatically generates a strategic search plan (5 searches) based on your research query
- **Parallel Web Search**: Performs multiple web searches concurrently for faster results
- **Comprehensive Report Generation**: Creates detailed, well-structured reports (5-10 pages, 1000+ words) in markdown format
- **Optional Email Delivery**: Optionally sends formatted HTML reports via SendGrid to user-provided email addresses
- **Real-time Progress Updates**: Streams status updates as the research progresses
- **Unified OpenAI Tracing**: All agent interactions (including clarification) are traced under a single trace ID for easier log management

## How It Works

The Research Helper uses a multi-stage agent pipeline with an optional clarification step:

0. **Clarifier Agent** (optional): Generates 3 clarifying questions to better understand and refine your research query. You can choose to answer these questions or skip directly to research.
1. **Planning Agent**: Analyzes your (refined) query and creates a strategic search plan with 5 targeted search terms and their reasoning
2. **Search Agent**: Performs web searches in parallel, summarizing results concisely (2-3 paragraphs, <300 words each)
3. **Writer Agent**: Synthesizes all search results into a comprehensive, well-structured markdown report with:
   - Detailed analysis (5-10 pages, 1000+ words)
   - Short summary
   - Follow-up research questions
4. **Email Agent** (optional): Formats the report as HTML and sends it via SendGrid to the user-provided email address

All agents use GPT-4o-mini and are orchestrated by the `ResearchManager` class, which handles the async workflow and progress streaming. When clarification is used, all agent interactions (including clarification) are traced under a single trace ID for unified log management.

## Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- SendGrid API key (for email delivery - optional)
- Email address for sender enabled via SendGrid

### Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

   Or using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using `uv`:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Set up environment variables:
   
   Create a `.env` file in the project root with the following:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   EMAIL_FROM=your_sender_email@example.com
   ```

### Running the App

```bash
python app.py
```

Or using `uv`:
```bash
uv run python app.py
```

The app will be available at `http://127.0.0.1:7860`

## Usage

1. Enter your research query in the text box (e.g., "Latest developments in quantum computing")
2. Choose how to proceed:
   - **Option A - Get Clarifying Questions** (recommended): Click "Get Clarifying Questions" to receive 3 questions that help refine your query. Answer them (optional) to improve research quality, then click "Run Research"
   - **Option B - Skip Clarification**: Click "Run Research" directly to start research with your original query
3. (Optional) Check "Send report via email" if you want to receive the report via email
   - If checked, you must provide your email address in the field that appears
   - The "Run Research" button will be disabled until you provide a valid email address when the checkbox is checked
4. Watch the progress updates as the system:
   - Plans searches
   - Performs web searches
   - Writes the report
   - (If email requested) Sends the email to your provided address
5. View the final report in the interface
6. (If email was requested) Check your email inbox for the formatted HTML report

### Query Clarification

- **Optional but recommended**: The clarification step helps refine your research query for better results
- Click "Get Clarifying Questions" to generate 3 targeted questions about your research topic
- Answering the questions is optional - you can skip them and still run research
- Your answers are incorporated into the refined query to improve search planning and report quality
- All clarification interactions are traced under the same trace ID as the main research for unified log management

### Email Delivery

- Email delivery is **optional** - you can view reports directly in the interface without email
- If you check "Send report via email", you must provide a valid email address
- The email will be sent to the address you provide (not to a default address)
- Reports are sent as formatted HTML emails via SendGrid

## Project Structure

```
research-helper/
├── app.py                      # Main Gradio application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── env.example                 # Example environment variables
├── research_agents/
│   ├── __init__.py            # Package initialization
│   ├── manager.py             # ResearchManager orchestrates the pipeline
│   ├── clarifier.py           # Clarifier agent (generates clarifying questions)
│   ├── planner.py             # Planning agent (creates search strategy)
│   ├── search.py              # Search agent (performs web searches)
│   ├── writer.py              # Writer agent (synthesizes reports)
│   └── email.py               # Email agent (sends reports)
└── README.md                   # This file
```

## Agent Details

### Clarifier Agent
- **Model**: GPT-4o-mini
- **Output**: `ClarifyingQuestions` with exactly 3 `ClarifyingQuestion` objects
- **Purpose**: Generates 3 targeted clarifying questions to better understand and refine research queries
- **Behavior**: Optional step - users can choose to get questions or skip directly to research
- **Tracing**: When used, clarification is traced under the same trace ID as the main research pipeline

### Planner Agent
- **Model**: GPT-4o-mini
- **Output**: `WebSearchPlan` with 5 `WebSearchItem` objects
- **Purpose**: Creates a strategic search plan with reasoning for each search term

### Search Agent
- **Model**: GPT-4o-mini
- **Tools**: `WebSearchTool` (low context size)
- **Output**: Concise summaries (2-3 paragraphs, <300 words)
- **Purpose**: Performs web searches and extracts key information

### Writer Agent
- **Model**: GPT-4o-mini
- **Output**: `ReportData` with:
  - `short_summary`: 2-3 sentence summary
  - `markdown_report`: Full detailed report (1000+ words)
  - `follow_up_questions`: Suggested topics for further research
- **Purpose**: Synthesizes search results into comprehensive reports

### Email Agent
- **Model**: GPT-4o-mini
- **Tools**: `send_email` function tool
- **Purpose**: Converts markdown reports to HTML and sends via SendGrid to user-provided email addresses
- **Behavior**: Only runs when the user opts in via the "Send report via email" checkbox and provides an email address

## Technologies

- **Gradio**: Web interface for the research assistant
- **OpenAI Agents**: Multi-agent framework for orchestration
- **SendGrid**: Email delivery service
- **Pydantic**: Data validation and structured outputs
- **Python-dotenv**: Environment variable management

## Configuration

You can customize the research behavior by modifying:

- **Number of clarifying questions**: Modify the `ClarifyingQuestions` model in `research_agents/clarifier.py` (currently fixed at 3)
- **Clarification instructions**: Adjust the agent instructions in `research_agents/clarifier.py`
- **Number of searches**: Change `HOW_MANY_SEARCHES` in `research_agents/planner.py` (default: 5)
- **Report length**: Modify instructions in `research_agents/writer.py`
- **Search summary length**: Adjust instructions in `research_agents/search.py`
- **Email formatting**: Customize the email agent instructions in `research_agents/email.py`

## Notes

- The system performs searches in parallel for efficiency
- Failed searches are gracefully handled (return `None` and continue)
- All agent interactions are traced via OpenAI's tracing system under a unified trace ID
- When clarification is used, the clarifier agent's trace is nested within the main Research trace for easier log management
- Reports are generated in markdown format and converted to HTML for email
- Query clarification is optional - users can skip it and run research directly with their original query
- Clarification answers are incorporated into the refined query to improve search planning and report quality
- Email delivery is optional - users can view reports in the interface without providing an email
- When email is requested, the user must provide their email address
- The "Run Research" button is automatically disabled if email is requested but no valid email address is provided

