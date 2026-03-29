"""Greenhouse API Ingester."""

import httpx
from typing import List, Optional
from datetime import datetime

from workers.ingestion.base_ingester import BaseIngester, RawJob, NormalizedJob


class GreenhouseIngester(BaseIngester):
    source_name = "greenhouse"
    base_url = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    def __init__(self, company_id: str):
        self.company_id = company_id
        self.url = self.base_url.format(company=company_id)

    async def fetch_raw_listings(self) -> List[RawJob]:
        """Fetch jobs from Greenhouse public Board API."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.url, params={"content": "true"})
            if resp.status_code != 200:
                return []

            data = resp.json()
            jobs = data.get("jobs", [])
            
            raw_jobs = []
            for j in jobs:
                try:
                    posted = None
                    if "updated_at" in j:
                        # greenhouse uses ISO format
                        posted_str = j["updated_at"].replace("Z", "+00:00")
                        posted = datetime.fromisoformat(posted_str).replace(tzinfo=None)

                    location = j.get("location", {}).get("name", "Remote")
                    is_remote = "remote" in location.lower() or "anywhere" in location.lower()

                    job = RawJob(
                        external_id=str(j["id"]),
                        title=j["title"],
                        company=self.company_id.replace("_", " ").title(),
                        location=location,
                        remote=is_remote,
                        description=j.get("content", ""),
                        source_url=j["absolute_url"],
                        posted_at=posted,
                    )
                    raw_jobs.append(job)
                except Exception:
                    continue

        return raw_jobs

    def normalize(self, raw: RawJob) -> NormalizedJob:
        """Normalize a raw Greenhouse job."""
        from bs4 import BeautifulSoup
        
        from html import unescape
        html_content = unescape(raw.description)

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
