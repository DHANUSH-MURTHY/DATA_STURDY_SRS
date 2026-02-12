"""
MCP Tool Server — exposes intelligence tools as an MCP-compatible layer.
Each tool returns structured JSON.
"""
import logging
from tools.web_search_tool import web_search
from tools.ir_scraper import scrape_ir

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ Demo data
DEMO_NEWS = {
    "Infosys": [
        {"title": "Infosys Expands Topaz AI Platform with Generative AI Studio",
         "snippet": "Infosys announced major upgrades to its Topaz AI platform, integrating NVIDIA hardware and OpenAI models for enterprise GenAI."},
        {"title": "Infosys Cobalt Partners with Microsoft Azure for Cloud Transformation",
         "snippet": "The Infosys Cobalt cloud platform deepens integration with Microsoft Azure, targeting digital transformation in manufacturing."},
    ],
    "TCS": [
        {"title": "TCS Launches AI.Cloud for Enterprise Intelligence",
         "snippet": "TCS introduced AI.Cloud, an integrated AI and cloud platform targeting mid-market enterprises across North America."},
        {"title": "TCS Wins Major Contract in UK Public Sector",
         "snippet": "TCS secured a £500M digital transformation contract with a UK government agency, expanding its European footprint."},
    ],
    "Wipro": [
        {"title": "Wipro ai360 Ecosystem Expands with IBM Partnership",
         "snippet": "Wipro's ai360 strategy now includes deeper IBM Watson integration for industry-specific AI solutions."},
        {"title": "Wipro FullStride Cloud Targets Healthcare Sector",
         "snippet": "Wipro announced new healthcare cloud solutions under its FullStride Cloud brand, targeting US hospital networks."},
    ],
    "HCLTech": [
        {"title": "HCLTech AI Force Integrates Google Cloud Vertex AI",
         "snippet": "HCLTech's AI Force platform now leverages Google Cloud Vertex AI for scalable enterprise ML deployments."},
        {"title": "HCLTech Expands Nordic Operations with New R&D Center",
         "snippet": "HCLTech opened a new R&D center in Stockholm, strengthening its position in the Nordic IT services market."},
    ],
    "Accenture": [
        {"title": "Accenture Invests $3B in AI, Partners with NVIDIA",
         "snippet": "Accenture announced a $3 billion investment in AI capabilities, including new NVIDIA-powered AI centers globally."},
        {"title": "Accenture Cloud First Surpasses $18B in Revenue",
         "snippet": "The Accenture Cloud First division reported strong growth, driven by multi-cloud transformation engagements."},
    ],
}

DEMO_IR = {
    "Infosys": "Revenue: $18.5B | Operating Margin: 21.5% | AI & Automation focus through Topaz platform. Key partnerships: NVIDIA, Microsoft, OpenAI. Geographic expansion in Nordics and Middle East.",
    "TCS":     "Revenue: $29.1B | Operating Margin: 24.3% | Cloud and AI integration through AI.Cloud. Key clients in BFSI and government. Strong presence in UK and North America.",
    "Wipro":   "Revenue: $11.3B | Operating Margin: 16.1% | ai360 strategy with IBM partnership. FullStride Cloud for industry verticals. Restructuring for growth.",
    "HCLTech": "Revenue: $13.7B | Operating Margin: 19.8% | AI Force and CloudSMART platforms. R&D expansion in Nordics. Strong engineering services segment.",
    "Accenture":"Revenue: $64.1B | Operating Margin: 15.2% | $3B AI investment. Cloud First at $18B. NVIDIA partnership for AI centers. Global presence across 120+ countries.",
}

DEMO_FINANCIALS = {
    "Infosys":  {"revenue": "$18.5B", "margin": "21.5%", "employees": "314,000", "ai_investment": "$2B", "yoy_growth": "4.2%"},
    "TCS":      {"revenue": "$29.1B", "margin": "24.3%", "employees": "601,000", "ai_investment": "$1.5B", "yoy_growth": "3.8%"},
    "Wipro":    {"revenue": "$11.3B", "margin": "16.1%", "employees": "234,000", "ai_investment": "$1B", "yoy_growth": "1.2%"},
    "HCLTech":  {"revenue": "$13.7B", "margin": "19.8%", "employees": "226,000", "ai_investment": "$1.2B", "yoy_growth": "5.1%"},
    "Accenture":{"revenue": "$64.1B", "margin": "15.2%", "employees": "743,000", "ai_investment": "$3B", "yoy_growth": "2.5%"},
}


# ------------------------------------------------------------------ Tools
async def crawl_company_news(company_name: str) -> list[dict]:
    """Crawl recent news for a company. Returns list of {title, snippet}."""
    logger.info("crawl_company_news: %s", company_name)
    # Try live search first, fall back to demo
    results = await web_search(f"{company_name} AI cloud strategy 2025 2026")
    if results:
        return results
    return DEMO_NEWS.get(company_name, [{"title": "No data", "snippet": ""}])


async def crawl_investor_relations(company_name: str) -> dict:
    """Crawl investor relations page. Returns {company, content}."""
    logger.info("crawl_investor_relations: %s", company_name)
    result = await scrape_ir(company_name)
    if result.get("content"):
        return result
    return {"company": company_name, "content": DEMO_IR.get(company_name, "")}


async def search_linkedin_talent_flow(company_a: str, company_b: str) -> dict:
    """Simulate talent flow analysis between two companies."""
    logger.info("search_linkedin_talent_flow: %s → %s", company_a, company_b)
    return {
        "source": company_a,
        "target": company_b,
        "talent_flow_direction": f"{company_a} → {company_b}",
        "estimated_transitions_12m": 245,
        "top_roles": ["Cloud Architect", "AI/ML Engineer", "Data Scientist", "DevOps Lead"],
        "insight": f"Moderate talent flow from {company_a} to {company_b} in cloud and AI roles, suggesting competitive hiring in GenAI space.",
    }


async def financial_extractor(company_name: str) -> dict:
    """Extract financial highlights for a company."""
    logger.info("financial_extractor: %s", company_name)
    return {
        "company": company_name,
        **DEMO_FINANCIALS.get(company_name, {"revenue": "N/A", "margin": "N/A"}),
    }


# ------------------------------------------------------------------ Registry
TOOL_REGISTRY = {
    "crawl_company_news": crawl_company_news,
    "crawl_investor_relations": crawl_investor_relations,
    "search_linkedin_talent_flow": search_linkedin_talent_flow,
    "financial_extractor": financial_extractor,
}
