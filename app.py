from flask import Flask, request, jsonify
import asyncio
import os
import json
from agent.search import search_linkedin_profiles
from agent.profile_fetcher import fetch_linkedin_profile
from agent.scorer import compute_fit_score
from agent.outreach_generator import generate_outreach
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


def jd_keywords_skills(job_desc: str):
    prompt = f"""
Extract 3-4 concise keywords from the job description below.
Return ONLY a JSON object with these keys:

  "role"        - primary job title or function (1-2 words)
  "location"    - city or region (short form, no country unless needed)
  "focus_area"  - technical focus or theme (1-2 words)
  "skill_list"  - list of all the skills mentioned in job description 

Example format:
{{
  "role": "role",
  "location": "location",
  "focus_area": "focus_area",
  "skill_list": []
}}

Job Description:
\"\"\"{job_desc}\"\"\"
"""
    default_terms = ['"software engineer"', '"machine learning"', '"ai"']
    default_skills = []

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_completion_tokens=256,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
        )

        kw_json = json.loads(completion.choices[0].message.content)

        terms = [
            kw_json.get("role", ""),
            kw_json.get("location", ""),
            kw_json.get("focus_area", "")
        ]
        skill_list = kw_json.get("skill_list", [])
        location = kw_json.get("location", "")

        quoted_terms = [f'"{t.strip()}"' for t in terms if t.strip()]
        query = "site:linkedin.com/in " + " ".join(quoted_terms) if quoted_terms else "site:linkedin.com/in"

    except Exception as e:
        print(f"Groq extraction failed: {e}")
        query = "site:linkedin.com/in " + " ".join(default_terms)
        skill_list = default_skills
        location = ""

    skill_list = [s.strip().lower() for s in skill_list if s.strip()]
    return skill_list, query.strip(), location


async def run_pipeline(job_description: str):
    skill_list, query, location = jd_keywords_skills(job_description)

    candidates = await search_linkedin_profiles(query)
    candidates = candidates

    enriched_candidates = []

    for idx, candidate in enumerate(candidates):
        profile_data = fetch_linkedin_profile(candidate["linkedin_url"])

        if not profile_data or "name" not in profile_data:
            continue

        profile_data["linkedin_url"] = candidate["linkedin_url"]
        profile_data["headline"] = candidate.get("headline", "")

        scored = compute_fit_score(profile_data, skill_list, location)
        outreach = generate_outreach(profile_data, job_description)

        enriched_candidates.append({
            "name": profile_data.get("name", profile_data.get("full_name", "")),
            "linkedin_url": profile_data["linkedin_url"],
            "fit_score": scored["fit_score"],
            "score_breakdown": scored["score_breakdown"],
            "outreach_message": outreach
        })

    result = {
        "candidates_found": len(enriched_candidates),
        "top_candidates": enriched_candidates
    }

    return result


@app.route('/run_pipeline', methods=['POST'])
def run_pipeline_api():
    data = request.get_json()
    job_description = data.get("job_description", "").strip()

    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    result = asyncio.run(run_pipeline(job_description))
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
