"""
FDA Data Ingestion Script
Loads Drug NDC and Drug Label records from local JSON files 
into ChromaDB Cloud as searchable vector embeddings.

Run from the backend/ root:
    python scripts/import_data.py
"""

import json
import sys
import os

# Allow imports from the backend/ root (e.g. config.chroma, utils.logger)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.chroma import get_collection
from utils.logger import logger

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
NDC_FILE = os.path.join(DATA_DIR, "drug-ndc.json")
LABEL_FILE = os.path.join(DATA_DIR, "drug-label.json")

BATCH_SIZE = 100          # Number of records per ChromaDB upsert call
NDC_LIMIT = 10_000        # Number of NDC records to ingest
LABEL_LIMIT = 20_000      # Number Label records to ingest 



def load_json(filepath: str) -> list[dict]:
    """Load the 'results' array from an openFDA JSON file."""
    logger.info(f"Loading {filepath} ...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("results", [])
    logger.info(f"Loaded {len(records):,} records from {os.path.basename(filepath)}")
    return records


def get_first(value, default: str = "") -> str:
    """
    openFDA fields are often arrays (e.g. ["Ibuprofen"]).
    This safely returns the first element as a plain string.
    """
    if isinstance(value, list) and value:
        return str(value[0]).strip()
    if isinstance(value, str):
        return value.strip()
    return default


def batch(items: list, size: int):
    """Split a list into chunks of `size` for batched processing."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


# Drug NDC builder 

def build_ndc_text(record: dict) -> str:
    """
    Combine the most useful NDC fields into a single searchable string.
    ChromaDB will embed this text so the chatbot can find it via similarity search.
    """
    brand      = record.get("brand_name", "")
    generic    = record.get("generic_name", "")
    labeler    = record.get("labeler_name", "")
    form       = record.get("dosage_form", "")
    routes     = ", ".join(record.get("route", []))
    prod_type  = record.get("product_type", "")
    mktg_cat   = record.get("marketing_category", "")
    ndc        = record.get("product_ndc", "")

    # Active ingredients: join name + strength pairs
    ingredients = record.get("active_ingredients", [])
    ingredient_str = "; ".join(
        f"{i.get('name', '')} {i.get('strength', '')}".strip()
        for i in ingredients
    )

    # Pharmacological class (mechanism + therapeutic class)
    pharm = "; ".join(record.get("pharm_class", []))

    return (
        f"Product NDC: {ndc} | "
        f"Brand: {brand} | "
        f"Generic: {generic} | "
        f"Labeler: {labeler} | "
        f"Type: {prod_type} | "
        f"Category: {mktg_cat} | "
        f"Form: {form} | "
        f"Route: {routes} | "
        f"Active Ingredients: {ingredient_str} | "
        f"Pharmacological Class: {pharm}"
    )


def build_ndc_metadata(record: dict) -> dict:
    """
    Store key fields as metadata so we can filter searches later.
    e.g. collection.query(where={"product_type": "HUMAN OTC DRUG"})
    """
    return {
        "source":           "drug_ndc",           # Distinguishes NDC vs Label records
        "product_ndc":      record.get("product_ndc", ""),
        "brand_name":       record.get("brand_name", ""),
        "generic_name":     record.get("generic_name", ""),
        "product_type":     record.get("product_type", ""),
        "dosage_form":      record.get("dosage_form", ""),
        "labeler_name":     record.get("labeler_name", ""),
        "marketing_category": record.get("marketing_category", ""),
    }


# Drug Label builder

def build_label_text(record: dict) -> str:
    """
    Combine the most clinically rich label sections into one searchable string.
    These are the sections users most commonly ask about:
    - What is it for? (indications)
    - Is it safe for me? (warnings, contraindications, pregnancy, pediatric)
    - How do I take it? (dosage)
    - What are the side effects? (adverse reactions)
    - What happens if I take too much? (overdosage)
    """
    openfda    = record.get("openfda", {})
    brand      = get_first(openfda.get("brand_name"))
    generic    = get_first(openfda.get("generic_name"))
    ndc        = get_first(openfda.get("product_ndc"))
    prod_type  = get_first(openfda.get("product_type"))

    purpose         = get_first(record.get("purpose"))
    indications     = get_first(record.get("indications_and_usage"))
    warnings        = get_first(record.get("warnings"))
    warnings2       = get_first(record.get("warnings_and_cautions"))
    boxed_warning   = get_first(record.get("boxed_warning"))
    do_not_use      = get_first(record.get("do_not_use"))
    stop_use        = get_first(record.get("stop_use"))
    contraindications = get_first(record.get("contraindications"))
    adverse         = get_first(record.get("adverse_reactions"))
    dosage          = get_first(record.get("dosage_and_administration"))
    overdosage      = get_first(record.get("overdosage"))
    pregnancy       = get_first(record.get("pregnancy"))
    preg_breast     = get_first(record.get("pregnancy_or_breast_feeding"))
    pediatric       = get_first(record.get("pediatric_use"))
    geriatric       = get_first(record.get("geriatric_use"))
    drug_interact   = get_first(record.get("drug_interactions"))
    description     = get_first(record.get("description"))

    # Truncate long sections to avoid huge embeddings (keep first 500 chars each)
    def trim(text: str, limit: int = 500) -> str:
        return text[:limit] if len(text) > limit else text

    return (
        f"Brand: {brand} | Generic: {generic} | NDC: {ndc} | Type: {prod_type} | "
        f"Purpose: {trim(purpose)} | "
        f"Indications: {trim(indications)} | "
        f"Warnings: {trim(warnings or warnings2)} | "
        f"Boxed Warning: {trim(boxed_warning)} | "
        f"Do Not Use: {trim(do_not_use)} | "
        f"Stop Use: {trim(stop_use)} | "
        f"Contraindications: {trim(contraindications)} | "
        f"Adverse Reactions: {trim(adverse)} | "
        f"Dosage: {trim(dosage)} | "
        f"Overdosage: {trim(overdosage)} | "
        f"Pregnancy: {trim(pregnancy or preg_breast)} | "
        f"Pediatric Use: {trim(pediatric)} | "
        f"Geriatric Use: {trim(geriatric)} | "
        f"Drug Interactions: {trim(drug_interact)} | "
        f"Description: {trim(description)}"
    )


def build_label_metadata(record: dict) -> dict:
    """Store identifiers and key names from the label for later filtering."""
    openfda = record.get("openfda", {})
    return {
        "source":       "drug_label",
        "label_id":     record.get("id", ""),
        "set_id":       record.get("set_id", ""),
        "brand_name":   get_first(openfda.get("brand_name")),
        "generic_name": get_first(openfda.get("generic_name")),
        "product_ndc":  get_first(openfda.get("product_ndc")),
        "product_type": get_first(openfda.get("product_type")),
        "effective_time": record.get("effective_time", ""),
    }


# Core ingestion logic

def ingest_records(
    records: list[dict],
    collection,
    build_text_fn,
    build_metadata_fn,
    id_field: str,
    source_name: str,
    limit: int,
) -> None:
    """
    Generic ingestion loop for any FDA dataset.
    - Uses `upsert` instead of `add` so re-running the script is safe
      (it won't create duplicates — it updates existing records instead).
    - Processes records in batches to avoid memory/timeout issues.
    """
    records = records[:limit]  # Limit the records
    total = len(records)
    logger.info(f"Ingesting {total:,} {source_name} records in batches of {BATCH_SIZE}...")

    ingested, skipped = 0, 0

    for batch_num, chunk in enumerate(batch(records, BATCH_SIZE), start=1):
        ids, documents, metadatas = [], [], []

        for record in chunk:
            # Use the record's unique ID field as the ChromaDB document ID
            doc_id = record.get(id_field, "")
            if not doc_id:
                skipped += 1
                continue  # Skip records with no ID — can't safely upsert them

            text = build_text_fn(record)
            if not text.strip():
                skipped += 1
                continue  # Skip records that produce empty text

            ids.append(str(doc_id))
            documents.append(text)
            metadatas.append(build_metadata_fn(record))

        if not ids:
            continue  # Nothing valid in this batch

        try:
            # upsert = insert if new, update if already exists
            collection.upsert(ids = ids, documents = documents, metadatas = metadatas)
            ingested += len(ids)
            logger.info(
                f"  Batch {batch_num} | {ingested:,}/{total:,} ingested | {skipped} skipped"
            )
        except Exception as e:
            logger.error(f"  Batch {batch_num} failed: {e}")
            skipped += len(ids)

    logger.info(
        f"Done ingesting {source_name}: {ingested:,} records saved, {skipped} skipped."
    )


def main() -> None:
    # Connect to ChromaDB Cloud and get (or create) the shared collection
    logger.info("Connecting to ChromaDB Cloud...")
    collection = get_collection()
    logger.info(f"Collection ready. Current document count: {collection.count():,}")

    # Step 1: Drug NDC
    logger.info("\n=== STEP 1: Drug NDC ===")
    ndc_records = load_json(NDC_FILE)
    ingest_records(
        records = ndc_records,
        collection = collection,
        build_text_fn = build_ndc_text,
        build_metadata_fn = build_ndc_metadata,
        id_field = "product_id",    # product_id is unique per NDC record
        source_name = "Drug NDC",
        limit = NDC_LIMIT,
    )

    # Step 2: Drug Labels
    logger.info("\n=== STEP 2: Drug Labels ===")
    label_records = load_json(LABEL_FILE)
    ingest_records(
        records = label_records,
        collection = collection,
        build_text_fn = build_label_text,
        build_metadata_fn = build_label_metadata,
        id_field = "id",            # id is unique per label record
        source_name = "Drug Label",
        limit = LABEL_LIMIT,
    )

    logger.info(f"\n All done! Total documents in ChromaDB: {collection.count():,}")


if __name__ == "__main__":
    main()
