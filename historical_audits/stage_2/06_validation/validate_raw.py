import os
import json
import csv
from pathlib import Path

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
RAW_JSON_DIR = WORKSPACE / "stage_2" / "02_extraction" / "raw_json"
VALIDATION_REPORT_PATH = WORKSPACE / "stage_2" / "06_validation" / "RAW_VALIDATION_REPORT.csv"

def classify_table(headers):
    # Flatten and lower
    headers_text = " ".join([str(h).lower() for h in headers if h])
    
    if "project id" in headers_text and "original cost" in headers_text:
        return "PROJECT_OBSERVATION_FLASH"
    if "project code" in headers_text and "date of approval" in headers_text:
        return "PROJECT_OBSERVATION_QPISR"
    if "sector" in headers_text and "achievement" in headers_text:
        return "SECTOR_PERFORMANCE"
    if "wpi" in headers_text or "index" in headers_text or "weight" in headers_text:
        return "EXTERNAL_ECONOMIC"
    return "UNKNOWN_GRAIN"

def validate_extraction():
    validation_records = []
    
    if not RAW_JSON_DIR.exists():
        print("Raw JSON directory not found.")
        return
        
    for json_file in RAW_JSON_DIR.glob("*.json"):
        source_id = json_file.stem
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            report_type = data['source_metadata']['report_type']
            tables = data.get('tables', [])
            
            table_classifications = {}
            total_valid_rows = 0
            
            for t in tables:
                headers = t.get('headers', [])
                grain = classify_table(headers)
                
                table_classifications[grain] = table_classifications.get(grain, 0) + 1
                if grain != "UNKNOWN_GRAIN":
                    total_valid_rows += len(t.get('rows', []))
            
            status = "PASS" if total_valid_rows > 0 else "FAIL_NO_VALID_DATA"
            
            validation_records.append({
                "source_id": source_id,
                "report_type": report_type,
                "tables_extracted": len(tables),
                "valid_tables": len(tables) - table_classifications.get("UNKNOWN_GRAIN", 0),
                "unknown_tables": table_classifications.get("UNKNOWN_GRAIN", 0),
                "total_valid_rows": total_valid_rows,
                "status": status,
                "notes": str(table_classifications)
            })
        except Exception as e:
            validation_records.append({
                "source_id": source_id,
                "report_type": "UNKNOWN",
                "tables_extracted": 0,
                "valid_tables": 0,
                "unknown_tables": 0,
                "total_valid_rows": 0,
                "status": "ERROR",
                "notes": str(e)
            })

    if validation_records:
        with open(VALIDATION_REPORT_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=validation_records[0].keys())
            writer.writeheader()
            writer.writerows(validation_records)
        print(f"Validation complete. Report at {VALIDATION_REPORT_PATH}")
    else:
        print("No validation records generated.")

if __name__ == "__main__":
    validate_extraction()
