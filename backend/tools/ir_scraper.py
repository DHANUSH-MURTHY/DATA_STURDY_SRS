"""
IR Scraper — BeautifulSoup-based scraper for investor-relations pages.
"""
import httpx
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

IR_URLS = {
    "Infosys":   "https://www.infosys.com/investors.html",
    "TCS":       "https://www.tcs.com/investor-relations",
    "Wipro":     "https://www.wipro.com/investors/",
    "HCLTech":   "https://www.hcltech.com/investors",
    "Accenture": "https://www.accenture.com/us-en/about/company/annual-report",
}


async def scrape_ir(company: str) -> dict:
    """Scrape investor relations page for a company. Returns {company, url, content}."""
    url = IR_URLS.get(company, "")
    if not url:
        return {"company": company, "url": "", "content": "", "error": "No IR URL configured"}
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        # Remove scripts/styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)[:5000]
        return {"company": company, "url": url, "content": text}
    except Exception as exc:
        logger.warning("IR scrape failed for %s: %s", company, exc)
        return {"company": company, "url": url, "content": "", "error": str(exc)}
