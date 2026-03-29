"""RSS/Atom Feed Ingester."""

import feedparser
from typing import List, Optional
from datetime import datetime

from workers.ingestion.base_ingester import BaseIngester, RawJob, NormalizedJob


class RSSIngester(BaseIngester):
    source_name = "rss"

    def __init__(self, feed_url: str, company_name: str):
        self.feed_url = feed_url
        self.company_name = company_name

    async def fetch_raw_listings(self) -> List[RawJob]:
        """Fetch and parse RSS/Atom feed."""
        import asyncio
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, self.feed_url)

        raw_jobs = []
        for entry in feed.entries:
            try:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])

                job = RawJob(
                    external_id=entry.id if hasattr(entry, "id") else entry.link,
                    title=entry.title,
                    company=self.company_name,
                    location="Location unspecified",
                    remote=False,
                    description=entry.summary if hasattr(entry, "summary") else getattr(entry, "description", ""),
                    source_url=entry.link,
                    posted_at=published,
                )
                raw_jobs.append(job)
            except Exception:
                continue

        return raw_jobs

    def normalize(self, raw: RawJob) -> NormalizedJob:
        """Normalize a raw RSS job."""
        from bs4 import BeautifulSoup

        desc_text = BeautifulSoup(raw.description, "html.parser").get_text(separator=" ")
        normalized_desc = desc_text.strip().replace("\n", " ")

        desc_lower = normalized_desc.lower()
        title_lower = raw.title.lower()
        is_remote = any(kw in f"{title_lower} {desc_lower}" for kw in ("remote", "telecommute", "work from home"))

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
            skills_extracted=[],  # Skills extracted in a later step
            experience_level=experience_level,
            salary_min=raw.salary_min,
            salary_max=raw.salary_max,
            posted_at=raw.posted_at,
        )
