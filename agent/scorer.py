import re

def normalize_text(text):
    return text.lower().strip() if text else ""

def score_education(education_list):
    elite_schools = ["mit", "stanford", "cmu", "harvard", "berkeley", "caltech", "oxford", "cambridge", "uiuc"]
    if not education_list:
        return 5.0

    score = 5.0
    for edu in education_list:
        school = normalize_text(edu.get("school", ""))
        if any(elite in school for elite in elite_schools):
            return 9.5
        elif "institute" in school or "university" in school:
            score = max(score, 7.5)
    return score

def score_trajectory(experience_list):
    if not experience_list:
        return 5.0

    years = []
    for exp in experience_list:
        dur = exp.get("duration", "")
        match = re.search(r"(\d+) yr", dur)
        if match:
            years.append(int(match.group(1)))
        elif "mos" in dur:
            years.append(0.5)

    if len(years) < 2:
        return 6.0
    if sorted(years) == years:
        return 8.0
    return 6.5

def score_company(experience_list):
    top_companies = ["google", "meta", "amazon", "microsoft", "openai", "nvidia", "apple"]
    relevant_industries = ["ai", "llm", "machine learning", "developer tools"]

    for exp in experience_list:
        company = normalize_text(exp.get("company", ""))
        title = normalize_text(exp.get("title", ""))
        if any(tc in company for tc in top_companies):
            return 9.5
        if any(ind in company or ind in title for ind in relevant_industries):
            return 7.5

    return 6.0

def score_skills(candidate_skills, skill_list):

    if not candidate_skills or not skill_list:
        return 5.0  # neutral score if either is empty

    # Normalize and lowercase all skills
    norm_candidate_skills = {normalize_text(skill) for skill in candidate_skills}
    norm_required_skills = {normalize_text(skill) for skill in skill_list}

    # Count how many required skills match
    matched = norm_candidate_skills.intersection(norm_required_skills)
    match_ratio = len(matched) / len(norm_required_skills)

    # Dynamic scoring
    if match_ratio >= 0.75:
        return 9.5
    elif match_ratio >= 0.5:
        return 8.0
    elif match_ratio >= 0.3:
        return 6.5
    elif match_ratio > 0:
        return 5.5
    else:
        return 5.0


def score_location(candidate_location, job_location):

    if not candidate_location or not job_location:
        return 5.0

    cand_loc = normalize_text(candidate_location)
    job_loc = normalize_text(job_location)

    # Exact match
    if job_loc in cand_loc or cand_loc in job_loc:
        return 10.0

    # Broader region match (e.g., city inside state or metro area)
    if any(area in cand_loc for area in job_loc.split()):
        return 8.0

    # Remote or hybrid scenarios
    if "remote" in cand_loc or "hybrid" in cand_loc:
        return 6.0

    return 5.0  # fallback default


def score_tenure(experience_list):
    if not experience_list:
        return 5.0

    avg_months = 0
    for exp in experience_list:
        dur = exp.get("duration", "")
        yrs = re.findall(r"(\d+)\s*yr", dur)
        mos = re.findall(r"(\d+)\s*mo", dur)

        months = 0
        if yrs:
            months += int(yrs[0]) * 12
        if mos:
            months += int(mos[0])

        avg_months += months

    avg_months = avg_months / len(experience_list)
    if avg_months >= 24:
        return 9.0
    elif avg_months >= 12:
        return 7.5
    elif avg_months >= 6:
        return 6.0
    return 4.0

def compute_fit_score(candidate, jd_keywords, location):
    edu_score = score_education(candidate.get("education", []))
    traj_score = score_trajectory(candidate.get("experience", []))
    comp_score = score_company(candidate.get("experience", []))
    skill_score = score_skills(candidate.get("skills", []), jd_keywords)
    loc_score = score_location(candidate.get("location", ""), location)
    ten_score = score_tenure(candidate.get("experience", []))

    # Weighted average
    final_score = (
        edu_score * 0.20 +
        traj_score * 0.20 +
        comp_score * 0.15 +
        skill_score * 0.25 +
        loc_score * 0.10 +
        ten_score * 0.10
    )

    return {
        "name": candidate.get("name", ""),
        "linkedin_url": candidate.get("linkedin_url", ""),
        "fit_score": round(final_score, 2),
        "score_breakdown": {
            "education": round(edu_score, 1),
            "trajectory": round(traj_score, 1),
            "company": round(comp_score, 1),
            "skills": round(skill_score, 1),
            "location": round(loc_score, 1),
            "tenure": round(ten_score, 1)
        }
    }
