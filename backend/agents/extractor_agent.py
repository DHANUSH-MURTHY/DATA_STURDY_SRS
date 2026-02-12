"""
Extractor Agent — LLM-based entity extraction from crawled text.
Produces structured JSON for graph insertion.
"""
import json
import logging
from config import settings
from prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ Demo data
DEMO_EXTRACTIONS = {
    "Infosys": {
        "company": "Infosys",
        "offerings": ["Topaz", "Cobalt", "Infosys Nia", "Springboard"],
        "ai_brands": ["Topaz"],
        "cloud_brands": ["Cobalt"],
        "partnerships": ["NVIDIA", "Microsoft", "OpenAI", "Google Cloud"],
        "geographic_expansion": ["Nordics", "Middle East", "North America", "Europe"],
        "investments": [
            {"target": "NVIDIA", "type": "Technology Partnership", "details": "GPU infrastructure for Topaz AI platform"},
            {"target": "OpenAI", "type": "Integration", "details": "GPT models integrated into Topaz GenAI Studio"},
        ],
    },
    "TCS": {
        "company": "TCS",
        "offerings": ["AI.Cloud", "TCS CloudEX", "TCS Bancs", "ignio"],
        "ai_brands": ["AI.Cloud"],
        "cloud_brands": ["TCS CloudEX"],
        "partnerships": ["AWS", "Google Cloud", "Microsoft"],
        "geographic_expansion": ["UK", "North America", "Latin America"],
        "investments": [
            {"target": "ignio", "type": "Internal R&D", "details": "Cognitive automation platform"},
        ],
    },
    "Wipro": {
        "company": "Wipro",
        "offerings": ["ai360", "FullStride Cloud", "Wipro Holmes", "LAUNCHPAD"],
        "ai_brands": ["ai360"],
        "cloud_brands": ["FullStride Cloud"],
        "partnerships": ["IBM", "ServiceNow", "Palo Alto Networks"],
        "geographic_expansion": ["North America", "Europe"],
        "investments": [
            {"target": "IBM Watson", "type": "Strategic Alliance", "details": "Industry-specific AI solutions"},
        ],
    },
    "HCLTech": {
        "company": "HCLTech",
        "offerings": ["AI Force", "CloudSMART", "HCL DRYiCE", "Supercharging"],
        "ai_brands": ["AI Force"],
        "cloud_brands": ["CloudSMART"],
        "partnerships": ["Microsoft", "Google Cloud", "SAP"],
        "geographic_expansion": ["Nordics", "North America", "Japan"],
        "investments": [
            {"target": "Google Cloud Vertex AI", "type": "Integration", "details": "Scalable enterprise ML"},
        ],
    },
    "Accenture": {
        "company": "Accenture",
        "offerings": ["AI Navigator", "Cloud First", "Accenture DevOps Platform", "myWizard"],
        "ai_brands": ["AI Navigator"],
        "cloud_brands": ["Cloud First"],
        "partnerships": ["AWS", "Salesforce", "NVIDIA", "Microsoft"],
        "geographic_expansion": ["Global"],
        "investments": [
            {"target": "NVIDIA", "type": "Strategic Investment", "details": "$3B AI investment including NVIDIA AI centers"},
            {"target": "AI Startups", "type": "Venture Arm", "details": "Accenture Ventures portfolio in GenAI"},
        ],
    },
}


async def extract_entities(company: str, raw_text: str) -> dict:
    """Extract structured entities from raw text using LLM (or demo fallback)."""
    is_ollama = settings.LLM_PROVIDER == "ollama"
    if settings.DEMO_MODE or (not is_ollama and not settings.OPENAI_API_KEY and not settings.GEMINI_API_KEY):
        logger.info("Using demo extraction for %s", company)
        return DEMO_EXTRACTIONS.get(company, {"company": company, "offerings": [], "ai_brands": [], "cloud_brands": [], "partnerships": [], "geographic_expansion": [], "investments": []})

    try:
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY)
        elif settings.LLM_PROVIDER == "ollama":
            from langchain_ollama import ChatOllama
            llm = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL, temperature=0)
        else:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, google_api_key=settings.GEMINI_API_KEY)

        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=EXTRACTION_USER_PROMPT.format(company=company, text=raw_text)),
        ]
        response = await llm.ainvoke(messages)
        return json.loads(response.content)
    except Exception as exc:
        logger.error("LLM extraction failed for %s: %s", company, exc)
        return DEMO_EXTRACTIONS.get(company, {"company": company, "offerings": []})


def entities_to_triples(extraction: dict) -> list[tuple]:
    """Convert extracted entities into graph triples."""
    company = extraction.get("company", "Unknown")
    triples = []

    for offering in extraction.get("offerings", []):
        triples.append(("Company", company, "OFFERS", "Product", offering))
    for brand in extraction.get("ai_brands", []):
        triples.append(("Company", company, "OFFERS", "Product", brand))
    for brand in extraction.get("cloud_brands", []):
        triples.append(("Company", company, "OFFERS", "Product", brand))
    for partner in extraction.get("partnerships", []):
        triples.append(("Company", company, "PARTNERS_WITH", "Partner", partner))
    for region in extraction.get("geographic_expansion", []):
        triples.append(("Company", company, "OPERATES_IN", "Region", region))
    for inv in extraction.get("investments", []):
        triples.append(("Company", company, "INVESTS_IN", "Investment", inv.get("target", "")))

    # Deduplicate
    return list(set(triples))
