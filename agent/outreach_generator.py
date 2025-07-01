import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def generate_outreach(candidate: dict, job_description: str) -> str:
    prompt = f"""
You are a recruiter at a top AI company.

Write a short, professional, and personalized LinkedIn message to this candidate:
Name: {candidate['name']}
Location: {candidate.get('location')}
Headline: {candidate.get('headline')}
Experience: {', '.join([exp.get('title', '') + ' at ' + exp.get('company', '') for exp in candidate.get('experience', [])[:2]])}
Skills: {', '.join(candidate.get('skills', [])[:5])}

Job Description Summary: {job_description}

The message should:
- Be warm and tailored to the profile
- Mention a couple of unique things from the candidate's profile
- Explain why this job is a good fit
- Be under 700 characters
- Avoid sounding like a generic cold message

Return only the message in plain text.
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()
