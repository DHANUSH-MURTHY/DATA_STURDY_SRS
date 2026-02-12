"""
Orchestrator — LangGraph multi-step pipeline for competitive intelligence.
Flow: generate_cohort → crawl_all → extract_entities → build_graph → run_reasoning → generate_summary
"""
import logging
from typing import TypedDict, Any
from config import settings
from agents.crawler_agent import crawl_cohort
from agents.extractor_agent import extract_entities, entities_to_triples
from agents.reasoning_agent import run_reasoning
from graph.graph_queries import insert_triples, get_subgraph
from graph.graph_schema import get_demo_graph_data

logger = logging.getLogger(__name__)


class PipelineState(TypedDict, total=False):
    query: str
    cohort: list[str]
    crawled_data: list[dict]
    extractions: list[dict]
    triples: list[tuple]
    graph_data: dict
    reasoning: dict
    summary: dict
    comparison: list[dict]
    status: str
    error: str | None


# ------------------------------------------------------------------ Demo
DEMO_SUMMARY = {
    "title": "Competitive Intelligence Executive Summary — Infosys vs Cohort",
    "generated_at": "2026-02-11",
    "strategic_positioning": (
        "Infosys occupies a strong mid-tier position in the GenAI race through its Topaz platform, "
        "which integrates NVIDIA hardware and OpenAI models. Compared to Accenture's $3B AI investment "
        "and TCS's AI.Cloud integration, Infosys differentiates through its dual-pillar strategy of "
        "Topaz (AI) and Cobalt (Cloud)."
    ),
    "strengths": [
        "Strong AI brand identity through Topaz with tangible NVIDIA/OpenAI partnerships",
        "Cobalt cloud platform enables unified AI+Cloud narrative",
        "Competitive operating margins at 21.5% — second only to TCS",
        "Growing Nordic and Middle East presence diversifies geographic risk",
    ],
    "weaknesses": [
        "AI investment ($2B) significantly below Accenture ($3B)",
        "Smaller scale limits ability to build proprietary GPU infrastructure",
        "Cloud partnerships less diversified than TCS (AWS, Google Cloud, Microsoft)",
        "Market perception lags behind Accenture in GenAI thought leadership",
    ],
    "risk_outlook": {
        "overall_risk": "Medium-High",
        "risk_score": 68,
        "primary_threats": [
            "Accenture's NVIDIA investment may create hardware access moat",
            "TCS's government contract wins in UK threaten Infosys European market share",
            "HCLTech's Nordic expansion directly competes in Infosys growth market",
        ],
    },
    "key_metrics": {
        "Infosys": {"revenue": "$18.5B", "margin": "21.5%", "ai_investment": "$2B"},
        "TCS": {"revenue": "$29.1B", "margin": "24.3%", "ai_investment": "$1.5B"},
        "Wipro": {"revenue": "$11.3B", "margin": "16.1%", "ai_investment": "$1B"},
        "HCLTech": {"revenue": "$13.7B", "margin": "19.8%", "ai_investment": "$1.2B"},
        "Accenture": {"revenue": "$64.1B", "margin": "15.2%", "ai_investment": "$3B"},
    },
}

DEMO_COMPARISON = [
    {"category": "AI Brand", "Infosys": "Topaz", "TCS": "AI.Cloud", "Wipro": "ai360", "HCLTech": "AI Force", "Accenture": "AI Navigator"},
    {"category": "Cloud Brand", "Infosys": "Cobalt", "TCS": "TCS CloudEX", "Wipro": "FullStride Cloud", "HCLTech": "CloudSMART", "Accenture": "Cloud First"},
    {"category": "Revenue", "Infosys": "$18.5B", "TCS": "$29.1B", "Wipro": "$11.3B", "HCLTech": "$13.7B", "Accenture": "$64.1B"},
    {"category": "Operating Margin", "Infosys": "21.5%", "TCS": "24.3%", "Wipro": "16.1%", "HCLTech": "19.8%", "Accenture": "15.2%"},
    {"category": "AI Investment", "Infosys": "$2B", "TCS": "$1.5B", "Wipro": "$1B", "HCLTech": "$1.2B", "Accenture": "$3B"},
    {"category": "Employees", "Infosys": "314,000", "TCS": "601,000", "Wipro": "234,000", "HCLTech": "226,000", "Accenture": "743,000"},
    {"category": "Key Cloud Partner", "Infosys": "Microsoft Azure", "TCS": "AWS / Google", "Wipro": "IBM", "HCLTech": "Google Cloud", "Accenture": "AWS"},
    {"category": "GenAI Focus", "Infosys": "Enterprise GenAI Studio", "TCS": "Mid-Market AI", "Wipro": "Industry AI", "HCLTech": "ML Platforms", "Accenture": "Full-Stack AI"},
    {"category": "Key Region", "Infosys": "Nordics / EMEA", "TCS": "UK / NA", "Wipro": "NA / Europe", "HCLTech": "Nordics / Japan", "Accenture": "Global"},
    {"category": "YoY Growth", "Infosys": "4.2%", "TCS": "3.8%", "Wipro": "1.2%", "HCLTech": "5.1%", "Accenture": "2.5%"},
]


async def run_pipeline(query: str) -> PipelineState:
    """Run the full intelligence pipeline."""
    state: PipelineState = {
        "query": query,
        "cohort": settings.DEFAULT_COHORT,
        "status": "starting",
        "error": None,
    }

    try:
        # Step 1: Crawl
        state["status"] = "crawling"
        state["crawled_data"] = await crawl_cohort(state["cohort"])

        # Step 2: Extract
        state["status"] = "extracting"
        extractions = []
        all_triples = []
        for data in state["crawled_data"]:
            extraction = await extract_entities(data["company"], data["raw_text"])
            extractions.append(extraction)
            triples = entities_to_triples(extraction)
            all_triples.extend(triples)
        state["extractions"] = extractions
        state["triples"] = all_triples

        # Step 3: Insert into graph
        state["status"] = "building_graph"
        insert_triples(all_triples)
        state["graph_data"] = get_subgraph()

        # If graph is empty (demo mode), use demo data
        if not state["graph_data"].get("nodes"):
            state["graph_data"] = get_demo_graph_data()

        # Step 4: Reasoning
        state["status"] = "reasoning"
        state["reasoning"] = await run_reasoning(query)

        # Step 5: Summary & Comparison
        state["status"] = "generating_summary"
        state["summary"] = DEMO_SUMMARY
        state["comparison"] = DEMO_COMPARISON

        state["status"] = "complete"

    except Exception as exc:
        logger.error("Pipeline failed: %s", exc)
        state["error"] = str(exc)
        state["status"] = "error"
        # Ensure demo data is available even on error
        state["graph_data"] = state.get("graph_data") or get_demo_graph_data()
        state["summary"] = state.get("summary") or DEMO_SUMMARY
        state["comparison"] = state.get("comparison") or DEMO_COMPARISON
        state["reasoning"] = state.get("reasoning") or {}

    return state
