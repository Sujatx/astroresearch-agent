from typing import List, Dict, Any
import os

from dotenv import load_dotenv
import google.generativeai as genai

# Load .env for GEMINI_API_KEY in local dev
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def generate_report(
    topic: str,
    papers: List[Dict[str, Any]],
    calculations: List[Dict[str, Any]],
) -> Dict[str, str]:
    """
    Ask Gemini to generate a structured scientific report.

    Returns:
      {
        "overview": "<main narrative + agreements + disagreements + key insights>",
        "future_work": "<gaps + hypotheses + concrete next steps>"
      }

    If anything fails, returns empty strings so caller can fall back.
    """
    if not api_key:
        # No key in this environment → keep API alive, just skip LLM
        return {"overview": "", "future_work": ""}

    # Build text describing the papers
    if papers:
        paper_text = "\n\n".join(
            (
                f"Title: {p.get('title', '')}\n"
                f"Authors: {', '.join(p.get('authors', []) or [])}\n"
                f"Published: {p.get('published', '')}\n"
                f"Abstract: {p.get('summary', '')}\n"
                f"URL: {p.get('url', '')}"
            )
            for p in papers
        )
    else:
        paper_text = "No papers were retrieved for this topic."

    # Build text describing any calculations
    if calculations:
        calc_text = "\n".join(
            f"{c.get('label', '')}: {c.get('value', '')} — {c.get('details', '')}"
            for c in calculations
        )
    else:
        calc_text = "No explicit calculations were performed."

    prompt = f"""
You are an expert astrophysics research assistant.

The user is asking about the topic:
"{topic}"

You are given a set of related papers:

PAPERS:
{paper_text}

You are also given some basic astrophysical calculations (if any):

CALCULATIONS:
{calc_text}

Your job is NOT just to summarize.
You must think like a researcher who is:
- Comparing the papers,
- Spotting agreements and disagreements,
- Identifying what is still unknown,
- And proposing realistic, testable new ideas.

Write a clear, research-style report in TWO parts:

=====================
1) OVERVIEW
=====================
In this section you MUST:
- Briefly explain the topic at a graduate-student level.
- Describe what the papers collectively say about the topic.
- Explicitly state where the papers AGREE (common results, patterns, shared conclusions).
- Explicitly state where they DISAGREE or TENSION exists (different methods, conflicting results, open controversy).
- Mention any important role for the given calculations (if they are relevant), or say they are generic if they do not tightly link to the papers.

This should feel like:
"Here is what we know, and here is how these works fit together (or clash)."

=====================
2) FUTURE_WORK
=====================
In this section you MUST:
- Identify concrete research GAPS suggested by the papers.
  (e.g. missing observations, poorly explored parameter ranges, missing simulations, unclear systematics, incomplete modelling.)
- Propose several realistic, topic-specific research directions.
- Include at least 2–3 specific, testable HYPOTHESES or questions, for example:
  - "If X is true, we should observe Y under conditions Z."
  - "A useful test would be to compare A vs B in regime C."
- Where appropriate, connect the gaps to potential future instruments, surveys, simulations, or theoretical developments.

IMPORTANT STYLE RULES:
- Do NOT use bullet points. Write in coherent paragraphs.
- Use the exact markers:

OVERVIEW:
<your text>

FUTURE_WORK:
<your text>

- Total length (both sections together) should be roughly 400–700 words.
- Stay grounded in the given papers; avoid hallucinating new fake papers.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""

        overview = ""
        future_work = ""

        if "FUTURE_WORK:" in text:
            before, after = text.split("FUTURE_WORK:", 1)
            overview = before.replace("OVERVIEW:", "").strip()
            future_work = after.strip()
        else:
            # If model ignores markers, treat everything as overview
            overview = text.strip()
            future_work = ""

        return {
            "overview": overview,
            "future_work": future_work,
        }

    except Exception as e:
        print("Gemini report error:", e)
        return {"overview": "", "future_work": ""}
