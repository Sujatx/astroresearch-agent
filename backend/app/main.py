from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for dev
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
    # TEMP: dummy data. This should match your frontend mock shape.
    dummy_paper = PaperSummary(
        title="Sample Paper 1",
        authors=["Author A", "Author B"],
        summary=(
            "Short summary of the first paper related to the topic. "
            "Real summaries will be generated later."
        ),
        url="https://arxiv.org",
        published=datetime(2025, 1, 1),
    )

    dummy_calc = CalculationResult(
        label="Example calculation",
        value="42 units",
        details="Placeholder astrophysics result for demo purposes.",
    )

    response = AnalyzeTopicResponse(
        topic=payload.topic,
        overview=(
            "This is a placeholder overview. Later this will come from "
            "arXiv + LLM through the backend."
        ),
        papers=[dummy_paper],
        calculations=[dummy_calc],
        future_work=(
            "This section will contain suggested future work based on the "
            "literature and calculations."
        ),
    )

    return response
