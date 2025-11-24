from datetime import datetime
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.arxiv_client import search_arxiv
from app.services.astro_math import (
    schwarzschild_radius_km,
    kepler_orbital_period_days,
)
from app.services.gemini_client import generate_report


app = FastAPI()

# CORS for frontend (dev + prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # wide open for now; can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------- MODELS ---------


class AnalyzeTopicRequest(BaseModel):
    topic: str
    max_papers: int = 3  # kept for compatibility, but we auto-decide internally


class PaperSummary(BaseModel):
    title: str
    authors: List[str]
    summary: str
    url: str
    published: datetime


class CalculationResult(BaseModel):
    label: str
    value: str
    details: str


class AnalyzeTopicResponse(BaseModel):
    topic: str
    overview: str
    papers: List[PaperSummary]
    calculations: List[CalculationResult]
    future_work: str


# --------- HELPERS ---------


def decide_max_papers(topic: str) -> int:
    """
    Automatically decide how many arXiv papers to fetch
    based on how broad/specific the topic looks.
    """
    t = topic.lower()

    # Extremely broad topics
    if any(x in t for x in ["universe", "cosmology", "astrophysics"]):
        return 8

    # Broad cosmology / fundamental physics topics
    if any(x in t for x in ["dark matter", "dark energy", "inflation", "structure formation"]):
        return 6

    # Medium complexity astrophysics topics
    if any(x in t for x in ["galaxy", "exoplanet", "planet", "accretion", "supernova"]):
        return 5

    # Narrow / specific topics
    return 3


# --------- ROUTES ---------


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze-topic", response_model=AnalyzeTopicResponse)
def analyze_topic(payload: AnalyzeTopicRequest):
    # 1) Decide how many papers to fetch based on topic
    max_p = decide_max_papers(payload.topic)

    # 2) Fetch papers from arXiv
    entries = search_arxiv(payload.topic, max_p)

    papers: List[PaperSummary] = []

    for e in entries:
        published_raw = e.get("published") or ""
        # arXiv uses ISO with 'Z' at the end -> convert to +00:00 for fromisoformat
        if published_raw.endswith("Z"):
            published_raw = published_raw.replace("Z", "+00:00")

        try:
            published_dt = datetime.fromisoformat(published_raw)
        except Exception:
            # fallback if parsing fails
            published_dt = datetime.utcnow()

        papers.append(
            PaperSummary(
                title=e.get("title", ""),
                authors=e.get("authors", []),
                summary=e.get("summary", ""),
                url=e.get("url", ""),
                published=published_dt,
            )
        )

    topic_lower = payload.topic.lower()
    calculations: List[CalculationResult] = []

    # 3) Topic-based calculations ONLY where it makes sense
    if "black hole" in topic_lower:
        mass_stellar = 10.0          # solar masses
        mass_supermassive = 4e6      # solar masses (like Sgr A*)

        rs_stellar_km = schwarzschild_radius_km(mass_stellar)
        rs_supermassive_km = schwarzschild_radius_km(mass_supermassive)

        calculations.append(
            CalculationResult(
                label="Schwarzschild radius (stellar-mass black hole)",
                value=f"{rs_stellar_km:,.2f} km",
                details=f"Event horizon radius for a {mass_stellar} M☉ black hole.",
            )
        )

        calculations.append(
            CalculationResult(
                label="Schwarzschild radius (supermassive black hole)",
                value=f"{rs_supermassive_km:,.2f} km",
                details=(
                    f"Event horizon radius for a {mass_supermassive:.1e} M☉ "
                    "supermassive black hole (similar to the Milky Way's center)."
                ),
            )
        )

    elif "orbit" in topic_lower or "exoplanet" in topic_lower or "planet" in topic_lower:
        p_1au_days = kepler_orbital_period_days(1.0, 1.0)
        p_5au_days = kepler_orbital_period_days(5.0, 1.0)

        calculations.append(
            CalculationResult(
                label="Orbital period at 1 AU",
                value=f"{p_1au_days:.1f} days",
                details="Approximate orbital period of an Earth-like orbit around a Sun-like star.",
            )
        )

        calculations.append(
            CalculationResult(
                label="Orbital period at 5 AU",
                value=f"{p_5au_days:.1f} days",
                details="Approximate orbital period for a Jupiter-like orbit around a Sun-like star.",
            )
        )

    else:
        # dark matter, inflation, CMB, etc → no random BH calcs
        calculations = []

    # 4) Call Gemini to generate overview + future_work
    papers_for_llm = []
    for p in papers:
        d = p.model_dump()
        d["published"] = p.published.isoformat()
        papers_for_llm.append(d)

    calcs_for_llm = [c.model_dump() for c in calculations]

    sections = generate_report(payload.topic, papers_for_llm, calcs_for_llm) or {}

    overview = sections.get("overview") or (
        f"This report is based on {len(papers)} arXiv result(s) for the topic "
        f"'{payload.topic}'. The summaries below are extracted directly from "
        "the arXiv abstracts."
    )

    future_work = sections.get("future_work") or (
        "Future work may include deeper analysis of recent literature, "
        "more detailed astrophysical modelling, and cross-correlation "
        "with multi-messenger or multi-wavelength observations where relevant."
    )

    return AnalyzeTopicResponse(
        topic=payload.topic,
        overview=overview,
        papers=papers,
        calculations=calculations,
        future_work=future_work,
    )
