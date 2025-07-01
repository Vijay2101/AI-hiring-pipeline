import os
import httpx
from typing import List, Dict



GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")


async def search_linkedin_profiles(query: str) -> List[Dict]:
    url = (
        f"https://customsearch.googleapis.com/customsearch/v1"
        f"?key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&q={query}"
    )
    print(url)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        print(response.status_code)
        print(response.json()) 
        data = response.json()
    
    results = []
    for item in data.get("items", []):
        results.append({
            "name": item.get("title", "").replace(" - LinkedIn", "").strip(),
            "linkedin_url": item.get("link"),
            "headline": item.get("snippet", "")
        })
    print("len:--------",len(results))
    return results
