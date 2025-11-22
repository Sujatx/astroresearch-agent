import httpx
from xml.etree import ElementTree as ET

ARXIV_API_URL = "https://export.arxiv.org/api/query"


def search_arxiv(topic: str, max_results: int = 3):
    """
    Search arXiv for a given topic and return a list of dicts:
    { title, summary, authors, url, published }
    If the request fails or times out, return an empty list instead of crashing.
    """
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results,
    }

    try:
        resp = httpx.get(
            ARXIV_API_URL,
            params=params,
            timeout=20.0,          # more relaxed timeout
            follow_redirects=True, # handle http -> https or other redirects
        )
        resp.raise_for_status()
    except httpx.RequestError as e:
        # Network / timeout error – log and return no results
        print(f"[arxiv] request error: {e}")
        return []
    except httpx.HTTPStatusError as e:
        # Non-2xx status – log and return no results
        print(f"[arxiv] bad status: {e}")
        return []

    # arXiv returns Atom XML
    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    results = []

    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip()
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
        published = entry.findtext("atom:published", default="", namespaces=ns).strip()

        link_el = entry.find("atom:link[@rel='alternate']", ns)
        url = link_el.get("href") if link_el is not None else ""

        authors = [
            a.findtext("atom:name", default="", namespaces=ns).strip()
            for a in entry.findall("atom:author", ns)
        ]

        results.append(
            {
                "title": title,
                "summary": summary,
                "published": published,
                "url": url,
                "authors": authors,
            }
        )

    return results
