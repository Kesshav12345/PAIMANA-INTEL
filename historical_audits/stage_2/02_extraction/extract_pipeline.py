import os
import csv
import json
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
MANIFEST_PATH = WORKSPACE / "stage_2" / "01_raw" / "SOURCE_MANIFEST.csv"
RAW_JSON_DIR = WORKSPACE / "stage_2" / "02_extraction" / "raw_json"
QUALITY_REPORT_PATH = WORKSPACE / "stage_2" / "02_extraction" / "EXTRACTION_QUALITY_REPORT.csv"

def extract_pdf_plumber(filepath, report_type):
    import pdfplumber
    extracted_tables = []
    status = "SUCCESS"
    notes = []
    pages_processed = 0
    pages_failed = 0
    
    try:
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables()
                    pages_processed += 1
                    for table_idx, table in enumerate(tables):
                        if not table: continue
                        
                        # Clean table (remove empty rows/cols if fully empty)
                        cleaned_table = [[str(cell).strip() if cell else "" for cell in row] for row in table]
                        
                        table_record = {
                            "page": page_num + 1,
                            "table_index": table_idx,
                            "headers": cleaned_table[0] if len(cleaned_table) > 0 else [],
                            "rows": cleaned_table[1:] if len(cleaned_table) > 1 else [],
                            "raw_content": cleaned_table
                        }
                        extracted_tables.append(table_record)
                except Exception as e:
                    pages_failed += 1
                    notes.append(f"Failed page {page_num+1}: {str(e)}")
                    status = "PARTIAL"
    except Exception as e:
        status = "FAILED"
        notes.append(f"Failed opening PDF: {str(e)}")
        
    return {
        "status": status,
        "tables": extracted_tables,
        "pages_processed": pages_processed,
        "pages_failed": pages_failed,
        "notes": "; ".join(notes)
    }

def extract_excel(filepath):
    import pandas as pd
    import numpy as np
    extracted_tables = []
    status = "SUCCESS"
    notes = []
    try:
        # Read all sheets
        xls = pd.ExcelFile(filepath)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df = df.replace({np.nan: None})
            
            headers = [str(c) for c in df.columns]
            rows = df.values.tolist()
            
            extracted_tables.append({
                "page": sheet_name,
                "table_index": 0,
                "headers": headers,
                "rows": rows,
                "raw_content": [headers] + rows
            })
    except Exception as e:
        status = "FAILED"
        notes.append(str(e))
        
    return {
        "status": status,
        "tables": extracted_tables,
        "pages_processed": 1,
        "pages_failed": 0,
        "notes": "; ".join(notes)
    }

def run_extraction():
    if not MANIFEST_PATH.exists():
        logger.error("Manifest not found.")
        return
        
    records = []
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)
        
    quality_records = []
    
    # Track which duplicates have been processed
    processed_hashes = {}
    
    for row in records:
        source_id = row['source_id']
        fhash = row['content_hash']
        filepath = WORKSPACE / row['relative_path']
        report_type = row['report_type']
        file_type = row['file_type']
        dup_group = row['duplicate_group']
        
        logger.info(f"Processing {source_id} ({filepath.name})")
        
        # Deduplication check at extraction level
        if fhash in processed_hashes:
            logger.info(f"Skipping duplicate hash {fhash}. Already processed as {processed_hashes[fhash]}")
            quality_records.append({
                "source_id": source_id,
                "status": "SKIPPED_DUPLICATE",
                "tables_extracted": 0,
                "pages_processed": 0,
                "pages_failed": 0,
                "canonical_source_id": processed_hashes[fhash],
                "notes": f"Duplicate of {processed_hashes[fhash]}"
            })
            continue
            
        if not filepath.exists():
            quality_records.append({
                "source_id": source_id,
                "status": "FAILED_NOT_FOUND",
                "tables_extracted": 0,
                "pages_processed": 0,
                "pages_failed": 0,
                "canonical_source_id": "",
                "notes": "File missing"
            })
            continue
            
        # Extraction logic
        if file_type == 'pdf':
            result = extract_pdf_plumber(filepath, report_type)
        elif file_type in ['xlsx', 'xls']:
            result = extract_excel(filepath)
        else:
            result = {
                "status": "SKIPPED_UNSUPPORTED",
                "tables": [],
                "pages_processed": 0,
                "pages_failed": 0,
                "notes": f"Unsupported type {file_type}"
            }
            
        # Save output
        if result["tables"]:
            output_path = RAW_JSON_DIR / f"{source_id}.json"
            with open(output_path, 'w', encoding='utf-8') as out_f:
                json.dump({
                    "source_metadata": row,
                    "extraction_metadata": {
                        "status": result["status"],
                        "pages_processed": result["pages_processed"],
                        "pages_failed": result["pages_failed"],
                        "tables_extracted": len(result["tables"]),
                    },
                    "tables": result["tables"]
                }, out_f, indent=2)
                
        processed_hashes[fhash] = source_id
        
        quality_records.append({
            "source_id": source_id,
            "status": result["status"],
            "tables_extracted": len(result["tables"]),
            "pages_processed": result["pages_processed"],
            "pages_failed": result["pages_failed"],
            "canonical_source_id": source_id,
            "notes": result["notes"]
        })

    # Write quality report
    if quality_records:
        with open(QUALITY_REPORT_PATH, 'w', newline='', encoding='utf-8') as qf:
            writer = csv.DictWriter(qf, fieldnames=quality_records[0].keys())
            writer.writeheader()
            writer.writerows(quality_records)
    logger.info(f"Extraction complete. Quality report written to {QUALITY_REPORT_PATH}")

if __name__ == "__main__":
    run_extraction()
