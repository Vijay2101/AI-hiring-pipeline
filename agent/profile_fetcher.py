import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def fetch_linkedin_profile(linkedin_url: str) -> dict:
    url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-linkedin-profile"

    querystring = {
        "linkedin_url": linkedin_url,
        "include_skills": "true",
        "include_certifications": "false",
        "include_publications": "false",
        "include_honors": "false",
        "include_volunteers": "false",
        "include_projects": "false",
        "include_patents": "false",
        "include_courses": "false",
        "include_organizations": "false",
        "include_profile_status": "false",
        "include_company_public_url": "false"
    }

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        print(f"[❌] Error {response.status_code}: {response.text}")
        return {}

    json_data = response.json()
    data = json_data.get("data", {})

    # Convert skills from "skill1|skill2|skill3" to list
    skills = data.get("skills", "")
    skills_list = [skill.strip() for skill in skills.split("|")] if isinstance(skills, str) else []

    return {
        "name": data.get("full_name"),
        "headline": data.get("headline"),
        "location": data.get("location"),
        "education": data.get("educations", []),
        "experience": data.get("experiences", []),
        "skills": skills_list
    }
