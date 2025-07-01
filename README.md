
# AI-Powered Hiring Agent



This project is an end-to-end AI-powered hiring pipeline that automates the process of:

- Understanding a job description

- Discovering top LinkedIn candidates

- Scoring them intelligently

- Generating personalized outreach messages

- Built with LLMs, async pipelines, and modular agents.


## Features

- **LLM-based JD Parsing**: Extracts structured data (role, location, focus, skill list) from raw job descriptions using Groq.

- **LinkedIn Candidate Discovery**: Uses custom Google search queries to surface real candidate profiles.

- **Profile Enrichment Agent**: Fetches simulated profile details (name, education, experience, skills, etc.).

- **Scoring Engine**: Dynamically evaluates candidate fit based on education, company, trajectory, location, skills, and tenure.

- **Outreach Generator**: Uses LLM to craft personalized cold messages.

- **Flask API**: Offers a simple /run_pipeline POST endpoint to automate the full process.


## Installation & Setup

Steps to Run

- Clone the repository
```bash
  git clone git@github.com:Vijay2101/AI-hiring-pipeline.git
  cd AI-hiring-pipeline
```

- Create .env
```bash
  GROQ_API_KEY=your_groq_key_here
  GOOGLE_API_KEY=your_google_key_here
  GOOGLE_CX=your_google_cx_key_here
  RAPIDAPI_KEY=your_rapidapi_key_here
```

- Install Requirements
```bash
  pip install -r requirements.txt
```
- Run Flask API
```bash
  python app.py
```

- Example API Request
```bash
  POST /run_pipeline
  Content-Type: application/json

  {
  "job_description": "Software Engineer, ML Research at Windsurf, Mountain View, CA..."
  }
```
## Tech Stack

- Python
- Flask
- Groq LLM (via groq client)
- AsyncIO
- Google Custom Search AP

