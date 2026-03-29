"""Lever API Ingester."""

import httpx
from typing import List, Optional
from datetime import datetime

from workers.ingestion.base_ingester import BaseIngester, RawJob, NormalizedJob


class LeverIngester(BaseIngester):
    source_name = "lever"
    base_url = "https://api.lever.co/v0/postings/{company}"

    def __init__(self, company_id: str):
        self.company_id = company_id
        self.url = self.base_url.format(company=company_id)

    async def fetch_raw_listings(self) -> List[RawJob]:
        """Fetch jobs from Lever public Postings API."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.url, params={"mode": "json"})
            if resp.status_code != 200:
                print(f"Lever API error: {resp.status_code}")
                return []

            jobs = resp.json()
            
            raw_jobs = []
            for j in jobs:
                try:
                    posted = None
                    if "createdAt" in j:
                        # lever returns unix timestamp in ms
                        posted = datetime.utcfromtimestamp(j["createdAt"] / 1000.0)

                    location = j.get("categories", {}).get("location", "Remote")
                    commitment = j.get("categories", {}).get("commitment", "")
                    workplace_type = j.get("workplaceType", "unspecified")
                    
                    is_remote = workplace_type.lower() == "remote" or "remote" in location.lower() or "anywhere" in location.lower()

                    # Lever description is plain text
                    description = j.get("descriptionPlain", j.get("description", ""))

                    job = RawJob(
                        external_id=j["id"],
                        title=j["text"],
                        company=self.company_id.replace("_", " ").title(),
                        location=location,
                        remote=is_remote,
                        description=description,
                        source_url=j["hostedUrl"],
                        posted_at=posted,
                    )
                    raw_jobs.append(job)
                except Exception as e:
                    print(f"Lever error processing job: {e}")
                    continue

        return raw_jobs

    def normalize(self, raw: RawJob) -> NormalizedJob:
        """Normalize a raw Lever job."""
        from bs4 import BeautifulSoup
        
        # Lever API often provides 'descriptionPlain' but we fallback to HTML
        html_content = raw.description
        desc_text = BeautifulSoup(html_content, "html.parser").get_text(separator=" ")
        normalized_desc = desc_text.strip().replace("\n", " ")

        desc_lower = normalized_desc.lower()
        title_lower = raw.title.lower()
        is_remote = raw.remote or any(kw in f"{title_lower} {desc_lower}" for kw in ("remote", "telecommute", "work from home"))

        content_hash = self.compute_hash(raw.title, raw.company, normalized_desc)
        experience_level = self._infer_experience_level(raw.title, normalized_desc)

        return NormalizedJob(
            source=self.source_name,
            source_url=raw.source_url,
            content_hash=content_hash,
            title=raw.title,
            company=raw.company,
            location=raw.location,
            remote=is_remote,
            description_raw=raw.description,
            description_normalized=normalized_desc,
            skills_extracted=[], 
            experience_level=experience_level,
            salary_min=raw.salary_min,
            salary_max=raw.salary_max,
            posted_at=raw.posted_at,
        )
