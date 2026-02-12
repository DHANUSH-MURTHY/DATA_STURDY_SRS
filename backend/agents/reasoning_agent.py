"""
Reasoning Agent — graph-based threat analysis and strategic inference.
"""
import json
import logging
from config import settings
from prompts.graph_reasoning_prompt import REASONING_SYSTEM_PROMPT, REASONING_USER_PROMPT
from prompts.graph_reasoning_prompt import NL_TO_CYPHER_SYSTEM, NL_TO_CYPHER_USER
from graph.graph_queries import get_subgraph

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ Demo
DEMO_REASONING = {
    "threat_level": "high",
    "strategic_impact": "Accenture's $3B AI investment with NVIDIA directly challenges Infosys Topaz's GenAI positioning by securing preferential access to NVIDIA's enterprise GPU infrastructure.",
    "competitive_risk_score": 72,
    "explanation": (
        "Accenture's aggressive investment in NVIDIA-powered AI centers creates a significant competitive threat to Infosys Topaz. "
        "While Infosys has a technology partnership with NVIDIA for its Topaz platform, Accenture's $3B commitment dwarfs Infosys's AI investment of ~$2B. "
        "This capital advantage allows Accenture to build dedicated GPU clusters that can offer clients faster GenAI deployment at scale.\n\n"
        "Infosys Topaz differentiates through its integration with OpenAI models and its Cobalt cloud synergy, but Accenture's Cloud First ($18B revenue) "
        "combined with NVIDIA hardware creates a vertically-integrated AI-to-cloud stack that is harder for Infosys to replicate.\n\n"
        "Key risk areas: (1) Enterprise clients may prefer Accenture's hardware-backed AI guarantees, (2) NVIDIA may prioritize Accenture for early access "
        "to new GPU architectures, (3) Talent competition will intensify as Accenture scales AI hiring."
    ),
    "key_relationships": [
        "Accenture -[INVESTS_IN]-> NVIDIA (Strategic Investment, $3B)",
        "Infosys -[OFFERS]-> Topaz -[USES]-> NVIDIA (Technology Partnership)",
        "Accenture -[OFFERS]-> AI Navigator (Competing AI brand)",
        "Infosys -[OFFERS]-> Cobalt (Cloud synergy advantage)",
    ],
    "recommendations": [
        "Deepen NVIDIA partnership with dedicated co-innovation labs for Topaz",
        "Accelerate proprietary model development to reduce NVIDIA dependency",
        "Leverage Cobalt cloud-native advantage with AI-as-a-Service pricing",
        "Target mid-market enterprises where Accenture's scale is less relevant",
    ],
}


async def run_reasoning(question: str, company: str | None = None) -> dict:
    """Perform graph-based reasoning to answer a strategic question."""
    # Get graph context
    graph_data = get_subgraph(company)
    graph_context = _graph_to_text(graph_data)

    is_ollama = settings.LLM_PROVIDER == "ollama"
    if settings.DEMO_MODE or (not is_ollama and not settings.OPENAI_API_KEY and not settings.GEMINI_API_KEY):
        logger.info("Using demo reasoning for: %s", question)
        return {**DEMO_REASONING, "question": question}

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
            SystemMessage(content=REASONING_SYSTEM_PROMPT),
            HumanMessage(content=REASONING_USER_PROMPT.format(
                graph_context=graph_context, question=question
            )),
        ]
        response = await llm.ainvoke(messages)
        return json.loads(response.content)
    except Exception as exc:
        logger.error("Reasoning failed: %s", exc)
        return {**DEMO_REASONING, "question": question, "error": str(exc)}


async def nl_to_cypher(question: str) -> str:
    """Convert natural-language question to Cypher (demo returns a sample)."""
    is_ollama = settings.LLM_PROVIDER == "ollama"
    if settings.DEMO_MODE or (not is_ollama and not settings.OPENAI_API_KEY and not settings.GEMINI_API_KEY):
        return "MATCH (a:Company)-[r]->(b) WHERE a.name = 'Infosys' RETURN a, r, b LIMIT 25"

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
            SystemMessage(content=NL_TO_CYPHER_SYSTEM),
            HumanMessage(content=NL_TO_CYPHER_USER.format(question=question)),
        ]
        response = await llm.ainvoke(messages)
        return response.content.strip()
    except Exception as exc:
        logger.error("NL-to-Cypher failed: %s", exc)
        return "MATCH (n) RETURN n LIMIT 25"


def _graph_to_text(graph_data: dict) -> str:
    """Convert graph data to readable text for LLM context."""
    lines = ["Knowledge Graph Context:", ""]
    lines.append("Nodes:")
    for node in graph_data.get("nodes", []):
        lines.append(f"  ({node['name']}) [{node['label']}]")
    lines.append("\nRelationships:")
    for edge in graph_data.get("edges", []):
        lines.append(f"  ({edge['source']}) -[{edge['relationship']}]-> ({edge['target']})")
    return "\n".join(lines)
