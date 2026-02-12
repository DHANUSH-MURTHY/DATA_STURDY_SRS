"""
FastAPI main server — Competitive Intelligence Orchestrator.
Endpoints: /analyze, /cohort, /graph/query, /export, /comparison, /health
"""
import csv
import io
import json
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from config import settings
from graph.neo4j_client import neo4j_client
from graph.graph_schema import init_schema, seed_graph, get_demo_graph_data
from graph.graph_queries import get_subgraph, find_common_partners, get_company_exposure, run_raw_cypher
from agents.orchestrator import run_pipeline, DEMO_SUMMARY, DEMO_COMPARISON
from agents.reasoning_agent import run_reasoning, nl_to_cypher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ App
app = FastAPI(
    title="Competitive Intelligence Orchestrator",
    description="Autonomous intelligence platform for IT services competitive analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    neo4j_client.connect()
    init_schema()
    seed_graph()
    logger.info("🚀 Competitive Intelligence Orchestrator started (demo_mode=%s)", settings.DEMO_MODE)


@app.on_event("shutdown")
async def shutdown():
    neo4j_client.close()


# ------------------------------------------------------------------ Health
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "demo_mode": settings.DEMO_MODE,
        "neo4j_connected": neo4j_client.is_connected,
        "llm_provider": settings.LLM_PROVIDER,
    }


# ------------------------------------------------------------------ Cohort
@app.get("/cohort")
async def get_cohort():
    return {"cohort": settings.DEFAULT_COHORT}


# ------------------------------------------------------------------ Analyze
@app.post("/analyze")
async def analyze(query: str = "How is Infosys positioning differently than TCS in GenAI for 2026?"):
    """Run full intelligence pipeline."""
    result = await run_pipeline(query)
    return result


# ------------------------------------------------------------------ Graph
@app.get("/graph")
async def get_graph(company: str = None):
    """Get graph data, optionally filtered by company."""
    data = get_subgraph(company)
    if not data.get("nodes"):
        data = get_demo_graph_data()
    return data


@app.post("/graph/query")
async def graph_query(question: str = "Show all Infosys relationships"):
    """Natural language or Cypher graph query."""
    # Try NL-to-Cypher
    cypher = await nl_to_cypher(question)
    results = run_raw_cypher(cypher)

    # Also run reasoning
    reasoning = await run_reasoning(question)

    return {
        "question": question,
        "generated_cypher": cypher,
        "query_results": results,
        "reasoning": reasoning,
    }


@app.get("/graph/common-partners")
async def common_partners(company_a: str = "Infosys", company_b: str = "Accenture"):
    partners = find_common_partners(company_a, company_b)
    return {"company_a": company_a, "company_b": company_b, "common_partners": partners}


@app.get("/graph/exposure")
async def entity_exposure(entity: str = "NVIDIA"):
    exposure = get_company_exposure(entity)
    return {"entity": entity, "exposure": exposure}


# ------------------------------------------------------------------ Comparison
@app.get("/comparison")
async def comparison():
    return {"comparison": DEMO_COMPARISON}


# ------------------------------------------------------------------ Summary
@app.get("/summary")
async def summary():
    return DEMO_SUMMARY


# ------------------------------------------------------------------ Export
@app.get("/export/{fmt}")
async def export(fmt: str):
    """Export data in CSV, JSON, or PDF format."""
    if fmt == "json":
        data = {
            "summary": DEMO_SUMMARY,
            "comparison": DEMO_COMPARISON,
            "graph": get_demo_graph_data(),
        }
        return JSONResponse(content=data, headers={
            "Content-Disposition": "attachment; filename=intelligence_report.json"
        })

    elif fmt == "csv":
        output = io.StringIO()
        if DEMO_COMPARISON:
            writer = csv.DictWriter(output, fieldnames=DEMO_COMPARISON[0].keys())
            writer.writeheader()
            writer.writerows(DEMO_COMPARISON)
        content = output.getvalue()
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=comparison_table.csv"},
        )

    elif fmt == "pdf":
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle("Title", parent=styles["Title"], textColor=HexColor("#7c3aed"), fontSize=18)
        story.append(Paragraph(DEMO_SUMMARY["title"], title_style))
        story.append(Spacer(1, 20))

        # Strategic Positioning
        story.append(Paragraph("<b>Strategic Positioning</b>", styles["Heading2"]))
        story.append(Paragraph(DEMO_SUMMARY["strategic_positioning"], styles["Normal"]))
        story.append(Spacer(1, 12))

        # Strengths
        story.append(Paragraph("<b>Strengths</b>", styles["Heading2"]))
        for s in DEMO_SUMMARY["strengths"]:
            story.append(Paragraph(f"• {s}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Weaknesses
        story.append(Paragraph("<b>Weaknesses</b>", styles["Heading2"]))
        for w in DEMO_SUMMARY["weaknesses"]:
            story.append(Paragraph(f"• {w}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Risk
        story.append(Paragraph("<b>Risk Outlook</b>", styles["Heading2"]))
        risk = DEMO_SUMMARY["risk_outlook"]
        story.append(Paragraph(f"Overall Risk: {risk['overall_risk']} (Score: {risk['risk_score']}/100)", styles["Normal"]))
        for t in risk["primary_threats"]:
            story.append(Paragraph(f"⚠ {t}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Comparison Table
        story.append(Paragraph("<b>Comparison Table</b>", styles["Heading2"]))
        if DEMO_COMPARISON:
            headers = list(DEMO_COMPARISON[0].keys())
            table_data = [headers] + [[row[h] for h in headers] for row in DEMO_COMPARISON]
            t = Table(table_data, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#7c3aed")),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f8f7ff"), HexColor("#ffffff")]),
            ]))
            story.append(t)

        doc.build(story)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=executive_summary.pdf"},
        )

    return {"error": f"Unsupported format: {fmt}. Use json, csv, or pdf."}


# ------------------------------------------------------------------ Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.BACKEND_PORT)
