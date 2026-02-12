"""
Crawler Agent — invokes MCP tools to gather news and IR data for each company.
"""
import logging
from tools.mcp_server import crawl_company_news, crawl_investor_relations, financial_extractor

logger = logging.getLogger(__name__)


async def crawl_company(company: str) -> dict:
    """Crawl all data sources for a single company. Returns combined raw data."""
    logger.info("Crawling data for %s", company)

    news = await crawl_company_news(company)
    ir = await crawl_investor_relations(company)
    financials = await financial_extractor(company)

    # Combine into a single text block for extraction
    news_text = "\n".join(
        f"- {n.get('title', '')}: {n.get('snippet', '')}" for n in news
    )
    ir_text = ir.get("content", "")

    combined_text = f"""
=== {company} — Company Intelligence ===

--- Recent News ---
{news_text}

--- Investor Relations ---
{ir_text}

--- Financial Highlights ---
Revenue: {financials.get('revenue', 'N/A')}
Operating Margin: {financials.get('margin', 'N/A')}
Employees: {financials.get('employees', 'N/A')}
AI Investment: {financials.get('ai_investment', 'N/A')}
YoY Growth: {financials.get('yoy_growth', 'N/A')}
"""
    return {
        "company": company,
        "raw_text": combined_text.strip(),
        "news": news,
        "ir": ir,
        "financials": financials,
    }


async def crawl_cohort(companies: list[str]) -> list[dict]:
    """Crawl all companies in the cohort."""
    results = []
    for company in companies:
        data = await crawl_company(company)
        results.append(data)
    return results
