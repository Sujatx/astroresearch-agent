import os
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

from dotenv import load_dotenv
import google.generativeai as genai

# Load local .env (for GEMINI_API_KEY when running locally)
load_dotenv()

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


# --------- LLM SUMMARIZATION (GEMINI) ---------


def summarize_with_gemini(
    topic: str,
    papers: List[PaperSummary],
    calculations: List[CalculationResult],
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # No key found -> don't break, just skip LLM
        return ""

    try:
        genai.configure(api_key=api_key)

        paper_text = "\n\n".join(
            f"Title: {p.title}\nAuthors: {', '.join(p.authors)}\nAbstract: {p.summary}"
            for p in papers
        ) or "No papers were retrieved for this topic."

        calc_text = "\n".join(
            f"{c.label}: {c.value} — {c.details}" for c in calculations
        ) or "No explicit calculations were performed."

        prompt = f"""
You are an astrophysics research assistant.

Summarize the following topic using the papers and calculations below.

Topic:
{topic}

Relevant Papers:
{paper_text}

Astrophysical Calculations:
{calc_text}

Write a coherent, research-style summary that:
- Explains the main ideas of the topic
- Synthesizes what the papers show collectively
- Mentions any differences in approaches if visible
- Connects the calculations to the physical picture
- Suggests a few directions for future research

Use clear, technical but readable language.
Aim for about 200–300 words.
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = getattr(response, "text", None)

        if not text:
            return ""

        return text.strip()

    except Exception as e:
        # Don't kill the API if Gemini fails
        print("Gemini summarization error:", e)
        return ""


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

    topic_lower = payload.topic.lower()
    calculations: List[CalculationResult] = []

    # 2) Topic-based calculations
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

    # 3) LLM-based overview (fallback to old logic if LLM fails)
    summary = summarize_with_gemini(payload.topic, papers, calculations)

    if summary:
        overview = summary
    else:
        overview = (
            f"This report is based on {len(papers)} arXiv result(s) for the topic "
            f"'{payload.topic}'. The summaries below are extracted directly from "
            "the arXiv abstracts."
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
