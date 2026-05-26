import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

FUSEKI_DATASET_URL = os.getenv("FUSEKI_URL")
FUSEKI_USER        = os.getenv("FUSEKI_USER")
FUSEKI_PASSWORD    = os.getenv("FUSEKI_PASSWORD")

FUSEKI_SPARQL_URL  = f"{FUSEKI_DATASET_URL}/sparql"
FUSEKI_UPDATE_URL  = f"{FUSEKI_DATASET_URL}/update"
FUSEKI_DATA_URL    = f"{FUSEKI_DATASET_URL}/data"

IMT_NS   = "http://imt-mines-ales.fr/ontology#"
IMTD_NS  = "http://imt-mines-ales.fr/data#"

KG_LLM_MODEL   = os.getenv("KG_LLM_MODEL")
KG_LLM_TEMP    = 0.0

SPARQL_RETRIES  = 1          # one self-correction attempt on bad SPARQL
MAX_PAGES       = None       # None = process all pages; set int to cap per PDF
