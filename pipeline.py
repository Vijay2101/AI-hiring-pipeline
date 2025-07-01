import json
import asyncio
from agent.search import search_linkedin_profiles
from agent.profile_fetcher import fetch_linkedin_profile
from agent.scorer import compute_fit_score
from agent.outreach_generator import generate_outreach
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

JOB_ID = "ml-research-windsurf"
OUTPUT_PATH = f"results/{JOB_ID}_results.json"

job_description = """
Software Engineer, ML Research
Windsurf
ID: SRN2025-10916
Windsurf
Software Engineer, ML Research
Windsurf • Full Time • Mountain View, CA • On-site • $140,000 – $300,000 + Equity
About the Company:
Windsurf (formerly Codeium) is a Forbes AI 50 company building the future of developer productivity through AI. With over 200 employees and $243M raised across multiple rounds including a Series C, Windsurf provides cutting-edge in-editor autocomplete, chat assistants, and full IDEs powered by proprietary LLMs. Their user base spans hundreds of thousands of developers worldwide, reflecting strong product-market fit and commercial traction.
Roles and Responsibilities:
Train and fine-tune LLMs focused on developer productivity
Design and prioritize experiments for product impact
Analyze results, conduct ablation studies, and document findings
Convert ML discoveries into scalable product features
Participate in the ML reading group and contribute to knowledge sharing
Job Requirements:
2+ years in software engineering with fast promotions
Strong software engineering and systems thinking skills
Proven experience training and iterating on large production neural networks
Strong GPA from a top CS undergrad program (MIT, Stanford, CMU, UIUC, etc.)
Familiarity with tools like Copilot, ChatGPT, or Windsurf is preferred
Deep curiosity for the code generation space
Excellent documentation and experimentation discipline
Prior experience with applied research (not purely academic publishing)
Must be able to work in Mountain View, CA full-time onsite
Excited to build product-facing features from ML research
"""

def jd_keywords_skills(job_desc: str) -> str:
    client = Groq()
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
    default_terms  = ['"software engineer"', '"machine learning"', '"ai"']
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

        # Assemble the search query
        terms = [
            kw_json.get("role", ""),
            kw_json.get("location", ""),
            kw_json.get("focus_area", "")
        ]
        skill_list = kw_json.get("skill_list",[])
        location = kw_json.get("location", "")
        # keep non‑empty terms, wrap each in quotes
        quoted_terms = [f'"{t.strip()}"' for t in terms if t.strip()]
        query = "site:linkedin.com/in " + " ".join(quoted_terms) if quoted_terms else "site:linkedin.com/in"

        skill_list = kw_json.get("skill_list", default_skills)

    except Exception as e:
        print(f"Groq extraction failed: {e}")
        query      = "site:linkedin.com/in " + " ".join(default_terms)
        skill_list = default_skills

    # final sanity‑check
    skill_list = [s.strip().lower() for s in skill_list if s.strip()]

    return skill_list, query.strip(), location


async def run_pipeline():
    skill_list, query, location=jd_keywords_skills(job_description)
    print("list: ", skill_list, "k: ",query,"location: ",location)
    print("Searching LinkedIn profiles...")
    candidates = await search_linkedin_profiles(query)

    print(f"Found {len(candidates)} profiles. Limiting to 15 for processing.")
    candidates = candidates

    enriched_candidates = []

    for idx, candidate in enumerate(candidates):
        print(f"\n Fetching profile {idx+1}/{len(candidates)}: {candidate['name']}")
        profile_data = fetch_linkedin_profile(candidate["linkedin_url"])

        if not profile_data or "name" not in profile_data:
            print("Skipping due to missing data.")
            continue

        profile_data["linkedin_url"] = candidate["linkedin_url"]
        profile_data["headline"] = candidate.get("headline", "")

        print("Scoring candidate...")
        scored = compute_fit_score(profile_data, skill_list, location)

        print("Generating outreach...")
        outreach = generate_outreach(profile_data, job_description)

        enriched_candidates.append({
            "name": profile_data.get("name", profile_data.get("full_name", "")),
            "linkedin_url": profile_data["linkedin_url"],
            "fit_score": scored["fit_score"],
            "score_breakdown": scored["score_breakdown"],
            "outreach_message": outreach
        })

    print(f"\n Saving top {len(enriched_candidates)} candidates to {OUTPUT_PATH}")
    # Ensure results/ folder exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    result = {
        "job_id": JOB_ID,
        "candidates_found": len(enriched_candidates),
        "top_candidates": enriched_candidates
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=4)

    print("Pipeline completed.")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
