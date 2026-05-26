"""
NL → SPARQL → Fuseki query executor.

generate_sparql()  : LLM translates natural language to SPARQL
execute_sparql()   : sends SPARQL SELECT to Fuseki, returns rows
nl_query()         : combines both with one self-correction retry
"""

import re
import json
import requests
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from mcp_server.config.kg_constants import (
    FUSEKI_SPARQL_URL, FUSEKI_USER, FUSEKI_PASSWORD,
    KG_LLM_MODEL, KG_LLM_TEMP, SPARQL_RETRIES,
)

# ---------------------------------------------------------------------------
# Compact ontology schema injected into every NL→SPARQL prompt
# ---------------------------------------------------------------------------
_SCHEMA = """
IMT Mines Alès Knowledge Graph — Ontology Schema
Prefixes: imt: <http://imt-mines-ales.fr/ontology#>   imtd: <http://imt-mines-ales.fr/data#>

Classes:
  imt:Module      top-level teaching unit (UE)
  imt:Course      sub-unit / matière inside a Module
  imt:Professor   teaching staff member
  imt:Evaluation  assessment component (exam, project, oral…)
  imt:Program     academic program  (2IA, PRISM, GC, I2ER, ISERM, TC)
  imt:Track       specialization    (iasd, il, img, con, gitm, sym, be, igo, ee, risk)
  imt:Semester    S5 S6 S8 S9 S10
  imt:Laboratory  research lab (LGI2P, LGEI, CHROME…)
  imt:FAQEntry    question–answer pair

Properties on TeachingUnit (Module or Course):
  unitCode, unitName, unitNameEN, ects(int), supervisedHours(int),
  personalWorkHours(int), rationale, objectives, keywords, prerequisiteText,
  lectureHours, workshopHours, labHours, projectHours, examHours
  → inSemester        → imt:Semester
  → partOfProgram     → imt:Program
  → partOfTrack       → imt:Track
  → taughtBy          → imt:Professor
  → responsibleProfessor → imt:Professor
  → hasEvaluation     → imt:Evaluation
  → hasPrerequisite   → imt:TeachingUnit

Course extra:
  coefficientInModule(decimal)
  → partOfModule → imt:Module

Module:
  → hasCourse → imt:Course

Professor: personName, email, phone, expertise
  → affiliatedTo → imt:Laboratory

Evaluation: evaluationType, evaluationCoefficient(decimal),
            administrationMode(individuelle|groupe), feedbackDelay

Program:   programCode, programName
Track:     trackCode, trackName  → trackBelongsToProgram → imt:Program
Semester:  semesterCode(S5/S6/S8/S9/S10), academicYear
Laboratory: labCode, labName
FAQEntry:  question, answer
""".strip()

_EXAMPLES = """
EXAMPLE 1
Question: How many ECTS credits does the deep learning module have?
SPARQL:
PREFIX imt: <http://imt-mines-ales.fr/ontology#>
SELECT ?name ?ects WHERE {
  ?m a imt:Module ; imt:unitName ?name ; imt:ects ?ects .
  FILTER(CONTAINS(LCASE(?name), "profond") || CONTAINS(LCASE(?name), "deep"))
}

EXAMPLE 2
Question: List all professors and the courses they are responsible for
SPARQL:
PREFIX imt: <http://imt-mines-ales.fr/ontology#>
SELECT ?profName ?courseName WHERE {
  ?c a imt:Course ; imt:unitName ?courseName ;
     imt:responsibleProfessor/imt:personName ?profName .
} ORDER BY ?profName

EXAMPLE 3
Question: What evaluation types are used in S9 courses?
SPARQL:
PREFIX imt: <http://imt-mines-ales.fr/ontology#>
SELECT DISTINCT ?evalType WHERE {
  ?c a imt:Course ; imt:inSemester/imt:semesterCode "S9" ;
     imt:hasEvaluation/imt:evaluationType ?evalType .
}

EXAMPLE 4
Question: Which courses require a project as part of evaluation?
SPARQL:
PREFIX imt: <http://imt-mines-ales.fr/ontology#>
SELECT ?courseName ?coef WHERE {
  ?c a imt:Course ; imt:unitName ?courseName ;
     imt:hasEvaluation ?e .
  ?e imt:evaluationType "projet" ; imt:evaluationCoefficient ?coef .
} ORDER BY DESC(?coef)
""".strip()

_NL_TO_SPARQL_SYSTEM = f"""You are a SPARQL expert for the IMT Mines Alès knowledge graph.

{_SCHEMA}

{_EXAMPLES}

Rules:
- Return ONLY the SPARQL query. No explanation, no markdown fences.
- Use PREFIX declarations at the top.
- Use property paths (e.g. imt:inSemester/imt:semesterCode) for conciseness.
- Use FILTER(CONTAINS(LCASE(?x), "keyword")) for partial text matching.
- Default to SELECT queries unless ASK or COUNT is clearly needed.
"""


def _extract_sparql(text: str) -> str:
    """Pull SPARQL out of LLM response — strip markdown if present."""
    text = text.strip()
    m = re.search(r"```(?:sparql)?\s*([\s\S]+?)\s*```", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # starts with PREFIX or SELECT directly
    m2 = re.search(r"(PREFIX[\s\S]+|SELECT[\s\S]+|ASK[\s\S]+|CONSTRUCT[\s\S]+)", text, re.IGNORECASE)
    if m2:
        return m2.group(1).strip()
    return text


def generate_sparql(question: str, llm: ChatGroq) -> str:
    """Translate a natural language question to a SPARQL query string."""
    response = llm.invoke([
        SystemMessage(content=_NL_TO_SPARQL_SYSTEM),
        HumanMessage(content=f"Question: {question}\nSPARQL:"),
    ])
    return _extract_sparql(response.content)


def execute_sparql(sparql: str) -> list[dict]:
    """
    Run a SPARQL SELECT against Fuseki.
    Returns a list of row dicts  {varName: value}.
    Raises ValueError on HTTP error.
    """
    resp = requests.get(
        FUSEKI_SPARQL_URL,
        params={"query": sparql},
        headers={"Accept": "application/sparql-results+json"},
        auth=(FUSEKI_USER, FUSEKI_PASSWORD),
        timeout=30,
    )
    if resp.status_code != 200:
        raise ValueError(f"Fuseki returned {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    rows = []
    for binding in data["results"]["bindings"]:
        rows.append({k: v["value"] for k, v in binding.items()})
    return rows


def nl_query(question: str, llm: ChatGroq) -> dict:
    """
    Full NL → SPARQL → Fuseki pipeline with one self-correction retry.
    Returns {"sparql": str, "rows": list[dict], "error": str|None}.
    """
    sparql = generate_sparql(question, llm)
    last_error = None

    for attempt in range(1 + SPARQL_RETRIES):
        try:
            rows = execute_sparql(sparql)
            return {"sparql": sparql, "rows": rows, "error": None}
        except ValueError as e:
            last_error = str(e)
            if attempt < SPARQL_RETRIES:
                # ask LLM to fix the broken query
                fix_prompt = (
                    f"The following SPARQL query failed with error:\n{last_error}\n\n"
                    f"Broken query:\n{sparql}\n\n"
                    f"Fix the query. Return ONLY the corrected SPARQL."
                )
                response = llm.invoke([
                    SystemMessage(content=_NL_TO_SPARQL_SYSTEM),
                    HumanMessage(content=fix_prompt),
                ])
                sparql = _extract_sparql(response.content)

    return {"sparql": sparql, "rows": [], "error": last_error}
