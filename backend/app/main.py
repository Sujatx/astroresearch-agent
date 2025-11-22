from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.services.arxiv_client import search_arxiv

from app.services.astro_math import (
    schwarzschild_radius_km,
    kepler_orbital_period_days,
)



app = FastAPI()

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------- MODELS ---------


class AnalyzeTopicRequest(BaseModel):
    topic: str
    max_papers: int = 3


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


# --------- ROUTES ---------


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze-topic", response_model=AnalyzeTopicResponse)
def analyze_topic(payload: AnalyzeTopicRequest):
    # 1) Fetch papers from arXiv
    entries = search_arxiv(payload.topic, payload.max_papers)

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

    # 2) Simple overview + dummy calculations for now
    overview = (
        f"This report is based on {len(papers)} arXiv result(s) for the topic "
        f"'{payload.topic}'. The summaries below are extracted directly from "
        "the arXiv abstracts."
    )

    topic_lower = payload.topic.lower()

    calculations: List[CalculationResult] = []

    if "black hole" in topic_lower:
        # Example: stellar-mass + supermassive black hole
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
        # Example orbital periods at 1 AU and 5 AU around a 1 M☉ star
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
        # Generic black hole calculation as a fallback
        mass_generic = 10.0
        rs_generic_km = schwarzschild_radius_km(mass_generic)

        calculations.append(
            CalculationResult(
                label="Schwarzschild radius (example)",
                value=f"{rs_generic_km:,.2f} km",
                details=(
                    f"Event horizon radius for a {mass_generic} M☉ black hole. "
                    "Used as a generic astrophysical scale for this topic."
                ),
            )
        )


    future_work = (
        "In future iterations, this agent will include more detailed reasoning, "
        "topic clustering, citation graph analysis, and astrophysical calculations "
        "tailored to the query."
    )

    return AnalyzeTopicResponse(
        topic=payload.topic,
        overview=overview,
        papers=papers,
        calculations=calculations,
        future_work=future_work,
    )
