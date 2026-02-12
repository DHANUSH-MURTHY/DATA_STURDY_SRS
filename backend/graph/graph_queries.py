"""
Graph queries — Cypher builders and natural-language-to-Cypher via LLM.
"""
from graph.neo4j_client import neo4j_client
from graph.graph_schema import get_demo_graph_data, SEED_TRIPLES
from config import settings


# ------------------------------------------------------------------ helpers
def _demo_subgraph(company: str | None = None) -> dict:
    data = get_demo_graph_data()
    if company:
        relevant_edges = [
            e for e in data["edges"]
            if company.lower() in e["source"].lower() or company.lower() in e["target"].lower()
        ]
        relevant_names = set()
        for e in relevant_edges:
            relevant_names.add(e["source"])
            relevant_names.add(e["target"])
        data["nodes"] = [n for n in data["nodes"] if n["name"] in relevant_names]
        data["edges"] = relevant_edges
    return data


# ------------------------------------------------------------------ public
def insert_triples(triples: list[tuple]):
    """Insert a list of (src_label, src_name, rel, tgt_label, tgt_name) tuples."""
    for src_label, src_name, rel, tgt_label, tgt_name in triples:
        cypher = (
            f"MERGE (a:{src_label} {{name: $src}}) "
            f"MERGE (b:{tgt_label} {{name: $tgt}}) "
            f"MERGE (a)-[:{rel}]->(b)"
        )
        neo4j_client.run_write(cypher, {"src": src_name, "tgt": tgt_name})


def get_subgraph(company: str | None = None) -> dict:
    """Return sub-graph centred on *company*. Falls back to demo data."""
    if not neo4j_client.is_connected:
        return _demo_subgraph(company)

    params = {}
    if company:
        cypher = """
            MATCH (a)-[r]->(b)
            WHERE a.name = $company OR b.name = $company
            RETURN labels(a)[0] AS src_label, a.name AS src,
                   type(r) AS rel,
                   labels(b)[0] AS tgt_label, b.name AS tgt
        """
        params = {"company": company}
    else:
        cypher = """
            MATCH (a)-[r]->(b)
            RETURN labels(a)[0] AS src_label, a.name AS src,
                   type(r) AS rel,
                   labels(b)[0] AS tgt_label, b.name AS tgt
            LIMIT 200
        """
    rows = neo4j_client.run_query(cypher, params)
    nodes, edges = {}, []
    for r in rows:
        nodes[r["src"]] = {"id": r["src"], "label": r["src_label"], "name": r["src"]}
        nodes[r["tgt"]] = {"id": r["tgt"], "label": r["tgt_label"], "name": r["tgt"]}
        edges.append({"source": r["src"], "target": r["tgt"], "relationship": r["rel"]})
    return {"nodes": list(nodes.values()), "edges": edges}


def find_common_partners(company_a: str, company_b: str) -> list[str]:
    if not neo4j_client.is_connected:
        partners_a = {t[4] for t in SEED_TRIPLES if t[1] == company_a and t[2] == "PARTNERS_WITH"}
        partners_b = {t[4] for t in SEED_TRIPLES if t[1] == company_b and t[2] == "PARTNERS_WITH"}
        return list(partners_a & partners_b)

    cypher = """
        MATCH (a:Company {name: $a})-[:PARTNERS_WITH]->(p:Partner)<-[:PARTNERS_WITH]-(b:Company {name: $b})
        RETURN p.name AS partner
    """
    return [r["partner"] for r in neo4j_client.run_query(cypher, {"a": company_a, "b": company_b})]


def get_company_exposure(entity: str) -> list[dict]:
    if not neo4j_client.is_connected:
        results = []
        for t in SEED_TRIPLES:
            if t[4] == entity or t[1] == entity:
                results.append({"company": t[1], "relationship": t[2], "entity": t[4]})
        return results

    cypher = """
        MATCH (c:Company)-[r]->(x {name: $entity})
        RETURN c.name AS company, type(r) AS relationship, x.name AS entity
    """
    return neo4j_client.run_query(cypher, {"entity": entity})


def run_raw_cypher(cypher: str) -> list[dict]:
    if not neo4j_client.is_connected:
        return [{"info": "Demo mode — raw Cypher not available. Showing full demo graph.", **get_demo_graph_data()}]
    return neo4j_client.run_query(cypher)
