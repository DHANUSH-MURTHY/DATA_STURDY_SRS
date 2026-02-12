"""
Web search tool — lightweight DuckDuckGo search via httpx.
"""
import httpx
import logging

logger = logging.getLogger(__name__)

SEARCH_URL = "https://html.duckduckgo.com/html/"


async def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo and return list of {title, url, snippet}."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.post(SEARCH_URL, data={"q": query, "b": ""})
            resp.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for r in soup.select(".result")[:max_results]:
            title_el = r.select_one(".result__title a")
            snippet_el = r.select_one(".result__snippet")
            if title_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": title_el.get("href", ""),
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })
        return results
    except Exception as exc:
        logger.warning("Web search failed: %s", exc)
        return []
