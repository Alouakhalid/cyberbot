import os
from tavily import TavilyClient

try:
    import streamlit as st
    _api_key = st.secrets["TAVILY_API_KEY"]
except Exception:
    _api_key = os.getenv("TAVILY_API_KEY", "")

tavily_client = TavilyClient(api_key=_api_key)

CYBER_DOMAINS = [
    "cve.mitre.org", "nvd.nist.gov", "exploit-db.com",
    "owasp.org", "sans.org", "threatpost.com", "bleepingcomputer.com",
    "hackerone.com", "portswigger.net", "thehackernews.com",
]


def search_cyber(query: str, max_results: int = 3) -> list[dict]:
    try:
        response = tavily_client.search(
            query=f"cybersecurity software engineering {query}",
            search_depth="advanced",
            max_results=max_results,
        )
        results = []
        for r in response.get("results", []):
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("content", "")[:1500],
            })
        return results
    except Exception as e:
        return [{"title": "Search Error", "url": "", "content": str(e)}]


def search_cve(cve_id: str) -> list[dict]:
    return search_cyber(f"{cve_id} vulnerability details exploit", max_results=5)


def format_search_context(results: list[dict]) -> str:
    if not results:
        return ""
    lines = ["[Web Search Results]"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}\n   {r['content']}\n   Source: {r['url']}")
    return "\n".join(lines)
