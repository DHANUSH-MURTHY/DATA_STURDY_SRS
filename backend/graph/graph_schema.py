"""
Graph schema — creates constraints, indexes, and base data in Neo4j.
"""
from graph.neo4j_client import neo4j_client

SCHEMA_STATEMENTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company)  REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product)  REQUIRE p.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (pr:Partner) REQUIRE pr.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Region)   REQUIRE r.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Investment) REQUIRE i.name IS UNIQUE",
    "CREATE INDEX IF NOT EXISTS FOR (c:Company)  ON (c.name)",
    "CREATE INDEX IF NOT EXISTS FOR (p:Product)  ON (p.name)",
]


def init_schema():
    """Run all schema statements (no-op in demo mode)."""
    for stmt in SCHEMA_STATEMENTS:
        neo4j_client.run_write(stmt)


SEED_TRIPLES = [
    # Infosys ecosystem
    ("Company", "Infosys",   "OFFERS",        "Product",  "Topaz"),
    ("Company", "Infosys",   "OFFERS",        "Product",  "Cobalt"),
    ("Product", "Topaz",     "USES",          "Partner",  "NVIDIA"),
    ("Product", "Topaz",     "USES",          "Partner",  "OpenAI"),
    ("Company", "Infosys",   "PARTNERS_WITH", "Partner",  "Microsoft"),
    ("Company", "Infosys",   "OPERATES_IN",   "Region",   "North America"),
    ("Company", "Infosys",   "OPERATES_IN",   "Region",   "Europe"),
    ("Company", "Infosys",   "OPERATES_IN",   "Region",   "Nordics"),
    # TCS ecosystem
    ("Company", "TCS",       "OFFERS",        "Product",  "AI.Cloud"),
    ("Company", "TCS",       "OFFERS",        "Product",  "TCS CloudEX"),
    ("Company", "TCS",       "PARTNERS_WITH", "Partner",  "AWS"),
    ("Company", "TCS",       "PARTNERS_WITH", "Partner",  "Google Cloud"),
    ("Company", "TCS",       "OPERATES_IN",   "Region",   "North America"),
    ("Company", "TCS",       "OPERATES_IN",   "Region",   "UK"),
    ("Company", "TCS",       "COMPETES_WITH", "Company",  "Infosys"),
    # Wipro ecosystem
    ("Company", "Wipro",     "OFFERS",        "Product",  "ai360"),
    ("Company", "Wipro",     "OFFERS",        "Product",  "FullStride Cloud"),
    ("Company", "Wipro",     "PARTNERS_WITH", "Partner",  "IBM"),
    ("Company", "Wipro",     "OPERATES_IN",   "Region",   "North America"),
    ("Company", "Wipro",     "COMPETES_WITH", "Company",  "Infosys"),
    # HCLTech ecosystem
    ("Company", "HCLTech",   "OFFERS",        "Product",  "AI Force"),
    ("Company", "HCLTech",   "OFFERS",        "Product",  "CloudSMART"),
    ("Company", "HCLTech",   "PARTNERS_WITH", "Partner",  "Microsoft"),
    ("Company", "HCLTech",   "PARTNERS_WITH", "Partner",  "Google Cloud"),
    ("Company", "HCLTech",   "OPERATES_IN",   "Region",   "North America"),
    ("Company", "HCLTech",   "OPERATES_IN",   "Region",   "Nordics"),
    ("Company", "HCLTech",   "COMPETES_WITH", "Company",  "Infosys"),
    # Accenture ecosystem
    ("Company", "Accenture", "OFFERS",        "Product",  "AI Navigator"),
    ("Company", "Accenture", "OFFERS",        "Product",  "Cloud First"),
    ("Company", "Accenture", "INVESTS_IN",    "Partner",  "NVIDIA"),
    ("Company", "Accenture", "PARTNERS_WITH", "Partner",  "AWS"),
    ("Company", "Accenture", "PARTNERS_WITH", "Partner",  "Salesforce"),
    ("Company", "Accenture", "OPERATES_IN",   "Region",   "Global"),
    ("Company", "Accenture", "COMPETES_WITH", "Company",  "Infosys"),
]


def seed_graph():
    """Insert seed triples into Neo4j (no-op in demo mode)."""
    for src_label, src_name, rel, tgt_label, tgt_name in SEED_TRIPLES:
        cypher = (
            f"MERGE (a:{src_label} {{name: $src}}) "
            f"MERGE (b:{tgt_label} {{name: $tgt}}) "
            f"MERGE (a)-[:{rel}]->(b)"
        )
        neo4j_client.run_write(cypher, {"src": src_name, "tgt": tgt_name})


def get_demo_graph_data() -> dict:
    """Return seed triples as a JSON-friendly structure for demo mode."""
    nodes, edges = {}, []
    for src_label, src_name, rel, tgt_label, tgt_name in SEED_TRIPLES:
        nodes[src_name] = {"id": src_name, "label": src_label, "name": src_name}
        nodes[tgt_name] = {"id": tgt_name, "label": tgt_label, "name": tgt_name}
        edges.append({"source": src_name, "target": tgt_name, "relationship": rel})
    return {"nodes": list(nodes.values()), "edges": edges}
