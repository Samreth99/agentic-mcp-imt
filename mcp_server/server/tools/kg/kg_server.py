"""
KG MCP Server — port 3001.
Thin FastMCP wrapper over triple_extractor and sparql_executor.

Tools:
  build_knowledge_graph(source)   PDF / directory → Fuseki
  query_knowledge_graph(question) NL → SPARQL → Fuseki → answer
  sparql_query(sparql)            direct SPARQL → Fuseki
  get_kg_statistics()             triple + entity counts from Fuseki
"""

import requests
from fastmcp import FastMCP

from mcp_server.server.tools.kg.triple_extractor import (
    make_llm, process_pdf, process_directory,
)
from mcp_server.server.tools.kg.sparql_executor import (
    nl_query, execute_sparql, generate_sparql,
)
from mcp_server.config.kg_constants import (
    FUSEKI_SPARQL_URL, FUSEKI_USER, FUSEKI_PASSWORD,
)

mcp = FastMCP("IMT Knowledge Graph", stateless_http=True)


@mcp.tool()
def build_knowledge_graph(source: str, source_type: str = "auto", force: bool = False) -> dict:
    """
    Ingest PDF documents into the IMT Knowledge Graph (Fuseki).

    Already-ingested PDFs are skipped automatically. Set force=True to re-process them.

    Args:
        source:      Path to a PDF file or a directory containing PDFs.
        source_type: "auto" (default), "file", or "directory".
        force:       Re-ingest even if already processed (default False).

    Returns:
        Stats dict with keys: pdfs, pages, inserted, failed, skipped.
    """
    from pathlib import Path

    llm = make_llm()
    path = Path(source)

    if source_type == "file" or (source_type == "auto" and path.is_file()):
        result = process_pdf(str(path), llm, force=force)
        result["pdfs"] = 1
        result["source"] = str(path)
        return result

    if source_type == "directory" or (source_type == "auto" and path.is_dir()):
        result = process_directory(str(path), llm, force=force)
        result["source"] = str(path)
        return result

    return {"error": f"Cannot determine source type for: {source}"}


@mcp.tool()
def query_knowledge_graph(question: str) -> dict:
    """
    Answer a natural language question by translating it to SPARQL and
    querying the IMT Knowledge Graph.

    Args:
        question: A natural language question about IMT courses, professors,
                  evaluations, programs, etc.

    Returns:
        Dict with: question, sparql (generated), rows (list of result dicts),
        answer (formatted string), error (None if successful).
    """
    llm = make_llm()
    result = nl_query(question, llm)

    rows = result["rows"]
    if rows:
        # Format rows into a readable answer string
        header = " | ".join(rows[0].keys())
        body = "\n".join(" | ".join(str(v)[:80] for v in row.values()) for row in rows[:50])
        answer = f"{header}\n{'-' * len(header)}\n{body}"
        if len(rows) > 50:
            answer += f"\n... ({len(rows)} total rows)"
    else:
        answer = "No results found." if result["error"] is None else f"Query failed: {result['error']}"

    return {
        "question": question,
        "sparql":   result["sparql"],
        "rows":     rows,
        "answer":   answer,
        "error":    result["error"],
    }


@mcp.tool()
def sparql_query(sparql: str) -> dict:
    """
    Execute a raw SPARQL SELECT query against the IMT Knowledge Graph.

    Args:
        sparql: A valid SPARQL 1.1 SELECT query.

    Returns:
        Dict with: rows (list of result dicts), count, error.
    """
    try:
        rows = execute_sparql(sparql)
        return {"rows": rows, "count": len(rows), "error": None}
    except ValueError as e:
        return {"rows": [], "count": 0, "error": str(e)}


@mcp.tool()
def get_kg_statistics(detail: str = "full") -> dict:
    """
    Return statistics about the IMT Knowledge Graph in Fuseki.

    Args:
        detail: "full" (default) returns triple count + entity counts per class.
                "total" returns only the total triple count.

    Returns:
        Dict with triple count and entity counts per class.
    """
    counts_query = """
PREFIX imt: <http://imt-mines-ales.fr/ontology#>
SELECT ?class (COUNT(?inst) AS ?count) WHERE {
  VALUES ?class {
    imt:Module imt:Course imt:Professor imt:Evaluation
    imt:Program imt:Track imt:Semester imt:Laboratory imt:FAQEntry
  }
  OPTIONAL { ?inst a ?class }
} GROUP BY ?class ORDER BY DESC(?count)
"""
    total_query = "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"

    try:
        total_rows = execute_sparql(total_query)
        total = int(total_rows[0]["n"]) if total_rows else 0

        by_class = {}
        if detail != "total":
            class_rows = execute_sparql(counts_query)
            by_class = {
                row["class"].split("#")[-1]: int(row["count"])
                for row in class_rows
                if int(row["count"]) > 0
            }

        return {
            "total_triples": total,
            "by_class":      by_class,
            "fuseki_url":    FUSEKI_SPARQL_URL,
            "error":         None,
        }
    except Exception as e:
        return {"total_triples": 0, "by_class": {}, "error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=3001)
