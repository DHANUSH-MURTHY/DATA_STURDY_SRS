"""
Extraction prompt — templates for LLM-based entity extraction from crawled data.
"""

EXTRACTION_SYSTEM_PROMPT = """You are a competitive intelligence analyst specializing in the IT services industry.
Given raw text about a company, extract structured strategic intelligence.

You MUST return valid JSON with exactly these keys:
{
  "company": "<company name>",
  "offerings": ["<product/service names>"],
  "ai_brands": ["<AI platform brand names>"],
  "cloud_brands": ["<cloud platform brand names>"],
  "partnerships": ["<partner company names>"],
  "geographic_expansion": ["<region names>"],
  "investments": [{"target": "<entity>", "type": "<investment type>", "details": "<brief>"}]
}

Rules:
- Only include items explicitly mentioned in the text.
- Normalise company names (e.g. "TCS" not "Tata Consultancy Services Ltd").
- Keep brand names exact (e.g. "Topaz", "AI.Cloud", "Cloud First").
- Return ONLY the JSON — no markdown fences, no commentary.
"""

EXTRACTION_USER_PROMPT = """Extract strategic intelligence from the following text about {company}:

---
{text}
---

Return the structured JSON now."""
