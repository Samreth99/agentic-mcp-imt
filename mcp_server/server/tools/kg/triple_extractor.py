"""
PDF → Fuseki triple extractor.

Pipeline per PDF:
  load pages (pymupdf) → per-page LLM extraction → SPARQL INSERT → Fuseki
"""

import re
import json
import requests
import pymupdf
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from mcp_server.config.kg_constants import (
    FUSEKI_UPDATE_URL, FUSEKI_USER, FUSEKI_PASSWORD,
    IMT_NS, IMTD_NS, KG_LLM_MODEL, KG_LLM_TEMP, MAX_PAGES,
)

# ---------------------------------------------------------------------------
# Integer and decimal properties — used for correct XSD typing in SPARQL
# ---------------------------------------------------------------------------
_INT_PROPS = {
    "ects", "supervisedHours", "personalWorkHours",
    "lectureHours", "workshopHours", "labHours",
    "projectHours", "examHours",
}
_DEC_PROPS = {"coefficientInModule", "evaluationCoefficient"}

_TYPE_TO_CLASS = {
    "Module":     "imt:Module",
    "Course":     "imt:Course",
    "Professor":  "imt:Professor",
    "Evaluation": "imt:Evaluation",
    "Program":    "imt:Program",
    "Track":      "imt:Track",
    "Laboratory": "imt:Laboratory",
    "FAQEntry":   "imt:FAQEntry",
}

_EXTRACTION_SYSTEM = """You extract structured academic data from IMT Mines Alès documents (French/English).

Return ONLY valid JSON — no explanation, no markdown. Schema:
{
  "entities": [
    {
      "type": "Module|Course|Professor|Evaluation|Program|Track|Laboratory|FAQEntry",
      "id":   "globally_unique_snake_case_id",
      "props": { "propertyName": value }
    }
  ],
  "relations": [
    { "subj": "id1", "pred": "predicateName", "obj": "id2" }
  ]
}

--- ONTOLOGY REFERENCE ---
Module/Course shared props (Module = top UE, Course = sub-unit/matière):
  unitCode, unitName, unitNameEN, ects(int), supervisedHours(int),
  personalWorkHours(int), rationale, objectives, summary, keywords,
  prerequisiteText, lectureHours(int), workshopHours(int), labHours(int),
  projectHours(int), examHours(int)
Course extra: coefficientInModule(decimal)
Professor:  personName, email, phone, expertise
Evaluation: evaluationType (one of: devoir_sur_table | projet | expose_oral |
            TP_note | controle_surprise | soutenance),
            evaluationCoefficient(decimal), administrationMode(individuelle|groupe),
            feedbackDelay, indicatorsEvaluated
Program:    programCode, programName
Track:      trackCode, trackName
Laboratory: labCode, labName
FAQEntry:   question, answer

Allowed relation predicates:
  hasCourse, partOfModule, responsibleProfessor, taughtBy, hasEvaluation,
  hasPrerequisite, inSemester, partOfProgram, partOfTrack, affiliatedTo,
  trackBelongsToProgram, blockBelongsToProgram, competencyInBlock

--- RULES ---
- Extract ONLY what is explicitly stated in the text.
- Make IDs globally unique: include content hints (e.g. "harispe_prof", "tc_5_1_module").
- ects / hours must be integers; coefficients must be decimals (0.75 not 75%).
- If nothing relevant: return {"entities": [], "relations": []}
- For FAQ text: extract FAQEntry entities with question + answer.
"""


def _make_id(raw: str) -> str:
    """Normalise an arbitrary string into a safe SPARQL local name."""
    slug = re.sub(r"[^a-z0-9]+", "_", raw.lower().strip())
    return slug[:60].strip("_") or "entity"


def _sparql_str(value: str) -> str:
    """Escape a string for use inside SPARQL double-quoted literals."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")


def _prop_to_turtle(prop: str, value) -> str | None:
    """Return a single `imt:prop value` triple fragment, or None if unrepresentable."""
    if value is None:
        return None
    if prop in _INT_PROPS:
        try:
            return f'    imt:{prop} {int(value)}'
        except (ValueError, TypeError):
            return None
    if prop in _DEC_PROPS:
        try:
            return f'    imt:{prop} "{float(value)}"^^xsd:decimal'
        except (ValueError, TypeError):
            return None
    return f'    imt:{prop} "{_sparql_str(str(value))}"'


def _entities_to_sparql_insert(entities: list[dict], relations: list[dict]) -> str | None:
    """Convert extracted JSON entities/relations into a SPARQL INSERT DATA block."""
    if not entities and not relations:
        return None

    lines = [
        "PREFIX imt:  <http://imt-mines-ales.fr/ontology#>",
        "PREFIX imtd: <http://imt-mines-ales.fr/data#>",
        "PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>",
        "",
        "INSERT DATA {",
    ]

    for ent in entities:
        raw_type = ent.get("type", "")
        cls = _TYPE_TO_CLASS.get(raw_type)
        if not cls:
            continue
        eid = _make_id(ent.get("id", raw_type))
        lines.append(f"  imtd:{eid} a {cls} ;")
        props = ent.get("props", {})
        prop_lines = [_prop_to_turtle(p, v) for p, v in props.items()]
        prop_lines = [l for l in prop_lines if l is not None]
        if prop_lines:
            for pl in prop_lines[:-1]:
                lines.append(pl + " ;")
            lines.append(prop_lines[-1] + " .")
        else:
            lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    for rel in relations:
        subj = _make_id(rel.get("subj", ""))
        pred = rel.get("pred", "")
        obj  = _make_id(rel.get("obj", ""))
        if subj and pred and obj:
            lines.append(f"  imtd:{subj} imt:{pred} imtd:{obj} .")

    lines.append("}")
    return "\n".join(lines)


def _call_fuseki_update(sparql: str) -> bool:
    """POST a SPARQL UPDATE to Fuseki. Returns True on success."""
    try:
        resp = requests.post(
            FUSEKI_UPDATE_URL,
            data={"update": sparql},
            auth=(FUSEKI_USER, FUSEKI_PASSWORD),
            timeout=30,
        )
        return resp.status_code in (200, 204)
    except requests.RequestException:
        return False


def _is_pdf_ingested(pdf_path: str) -> bool:
    """Check whether this PDF has already been recorded in Fuseki."""
    escaped = _sparql_str(pdf_path)
    sparql = (
        "PREFIX imt: <http://imt-mines-ales.fr/ontology#>\n"
        f'ASK {{ ?s imt:sourcePDF "{escaped}" }}'
    )
    try:
        resp = requests.get(
            FUSEKI_SPARQL_URL,
            params={"query": sparql},
            headers={"Accept": "application/sparql-results+json"},
            auth=(FUSEKI_USER, FUSEKI_PASSWORD),
            timeout=10,
        )
        return resp.status_code == 200 and resp.json().get("boolean", False)
    except Exception:
        return False


def _mark_pdf_ingested(pdf_path: str) -> None:
    """Record a sourcePDF triple in Fuseki so subsequent runs skip this file."""
    escaped = _sparql_str(pdf_path)
    sparql = (
        "PREFIX imt:  <http://imt-mines-ales.fr/ontology#>\n"
        "PREFIX imtd: <http://imt-mines-ales.fr/data#>\n"
        "INSERT DATA {\n"
        f'  imtd:ingestion_log imt:sourcePDF "{escaped}" .\n'
        "}"
    )
    _call_fuseki_update(sparql)


def _extract_json(text: str) -> dict:
    """Pull JSON from LLM response — handles raw JSON or ```json ... ``` blocks."""
    text = text.strip()
    # strip markdown code fence
    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        text = m.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # try to find the first {...} block
        m2 = re.search(r"\{[\s\S]+\}", text)
        if m2:
            try:
                return json.loads(m2.group(0))
            except json.JSONDecodeError:
                pass
    return {"entities": [], "relations": []}


def load_pdf_pages(pdf_path: str) -> list[str]:
    """Return a list of page texts from a PDF. Empty pages are skipped."""
    doc = pymupdf.open(pdf_path)
    pages = []
    limit = MAX_PAGES or len(doc)
    for i, page in enumerate(doc):
        if i >= limit:
            break
        text = page.get_text().strip()
        if len(text) > 80:   # skip near-blank pages
            pages.append(text)
    doc.close()
    return pages


def extract_triples_from_page(text: str, llm: ChatGroq) -> dict:
    """Ask the LLM to extract entities/relations from one page of text."""
    response = llm.invoke([
        SystemMessage(content=_EXTRACTION_SYSTEM),
        HumanMessage(content=f"Extract from this document page:\n\n{text[:4000]}"),
    ])
    return _extract_json(response.content)


def process_pdf(pdf_path: str, llm: ChatGroq, force: bool = False) -> dict:
    """
    Extract triples from all pages of a PDF and insert into Fuseki.
    Skips the file if it was already ingested (unless force=True).
    Returns {"pages": int, "inserted": int, "failed": int, "skipped": bool}.
    """
    if not force and _is_pdf_ingested(pdf_path):
        return {"pages": 0, "inserted": 0, "failed": 0, "skipped": True}

    pages = load_pdf_pages(pdf_path)
    inserted = failed = 0

    for page_text in pages:
        extracted = extract_triples_from_page(page_text, llm)
        sparql = _entities_to_sparql_insert(
            extracted.get("entities", []),
            extracted.get("relations", []),
        )
        if sparql is None:
            continue
        if _call_fuseki_update(sparql):
            inserted += 1
        else:
            failed += 1

    _mark_pdf_ingested(pdf_path)
    return {"pages": len(pages), "inserted": inserted, "failed": failed, "skipped": False}


def process_directory(dir_path: str, llm: ChatGroq, force: bool = False) -> dict:
    """Process all PDFs in a directory tree. Skips already-ingested files."""
    pdfs = list(Path(dir_path).rglob("*.pdf"))
    total = {"pdfs": len(pdfs), "pages": 0, "inserted": 0, "failed": 0, "skipped": 0}
    for pdf in pdfs:
        r = process_pdf(str(pdf), llm, force=force)
        if r.get("skipped"):
            total["skipped"] += 1
        else:
            total["pages"]    += r["pages"]
            total["inserted"] += r["inserted"]
            total["failed"]   += r["failed"]
    return total


def make_llm() -> ChatGroq:
    return ChatGroq(model=KG_LLM_MODEL, temperature=KG_LLM_TEMP)
