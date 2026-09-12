import os
import hashlib
import csv
import datetime
import re
from pathlib import Path

# Note: Using basic PyMuPDF (fitz) to get page counts, if available
try:
    import fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
PRIMARY_DIR = WORKSPACE / "Primary datasets"
SECONDARY_DIR = WORKSPACE / "Secondary dataset"
MANIFEST_PATH = WORKSPACE / "stage_2" / "01_raw" / "SOURCE_MANIFEST.csv"

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def classify_report(filename, filepath):
    filename_lower = filename.lower()
    
    # Report Type Classification
    if "flashreport" in filename_lower or "fr_" in filename_lower or "frapril" in filename_lower:
        report_type = "FLASH_REPORT"
        source_family = "PROJECT_MONITORING"
    elif "qpisr" in filename_lower:
        report_type = "QPISR"
        source_family = "PROJECT_MONITORING"
    elif "completereviewreport" in filename_lower or "reviewreport" in filename_lower:
        report_type = "SECTOR_PERFORMANCE_REVIEW"
        source_family = "SECTOR_PERFORMANCE"
    elif "index" in filename_lower or "ppi" in filename_lower or "wpi" in filename_lower:
        report_type = "ECONOMIC_INDEX"
        source_family = "EXTERNAL_DATA"
    else:
        report_type = "UNKNOWN"
        source_family = "UNKNOWN"
        
    # Historical classification
    is_historical = "archival" in str(filepath).lower()
    hist_class = "HISTORICAL" if is_historical else "CURRENT"
    
    # Attempt to extract report date from filename
    # e.g., "FlashReport_October_2025" -> "October 2025"
    report_date = ""
    month_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)[\s_]*(\d{4})?', filename_lower)
    if month_match:
        month = month_match.group(1).capitalize()
        year = month_match.group(2) if month_match.group(2) else ""
        report_date = f"{month} {year}".strip()
    
    return report_type, source_family, hist_class, report_date

def get_page_count(filepath):
    if not HAS_FITZ:
        return 0
    if filepath.suffix.lower() == '.pdf':
        try:
            doc = fitz.open(filepath)
            count = len(doc)
            doc.close()
            return count
        except Exception:
            return 0
    return 0

def build_manifest():
    manifest_records = []
    
    # Collect files
    target_dirs = [PRIMARY_DIR, SECONDARY_DIR]
    all_files = []
    for d in target_dirs:
        for root, _, files in os.walk(d):
            for f in files:
                all_files.append(Path(root) / f)
                
    # Group by hash to find duplicates
    hash_to_files = {}
    
    for file_id, filepath in enumerate(sorted(all_files), start=1):
        if filepath.name == ".DS_Store" or filepath.suffix.lower() not in ['.pdf', '.xlsx', '.csv', '.json', '.docx']:
            continue
            
        rel_path = filepath.relative_to(WORKSPACE)
        fhash = get_file_hash(filepath)
        fsize = filepath.stat().st_size
        
        if fhash not in hash_to_files:
            hash_to_files[fhash] = []
        hash_to_files[fhash].append(file_id)
        
        report_type, source_family, hist_class, report_date = classify_report(filepath.name, filepath)
        pages = get_page_count(filepath)
        
        record = {
            "source_id": f"SRC_{file_id:04d}",
            "filename": filepath.name,
            "relative_path": str(rel_path),
            "file_type": filepath.suffix.lower().replace('.', ''),
            "file_size": fsize,
            "content_hash": fhash,
            "source_family": source_family,
            "report_type": report_type,
            "report_date": report_date,
            "reporting_period": "",
            "publication_date": "",
            "revision_information": "",
            "historical_current_classification": hist_class,
            "duplicate_group": "", # To be filled
            "official_match": "",
            "extraction_status": "PENDING",
            "pages": pages,
            "tables_detected": 0,
            "figures_detected": 0,
            "extraction_method": "",
            "processing_version": "0.1.0",
            "processing_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_confidence": "HIGH",
            "notes": ""
        }
        manifest_records.append(record)
        
    # Assign duplicate groups
    dup_counter = 1
    for fhash, ids in hash_to_files.items():
        if len(ids) > 1:
            group_id = f"DUP_{dup_counter:03d}"
            for record in manifest_records:
                if int(record["source_id"].split("_")[1]) in ids:
                    record["duplicate_group"] = group_id
                    # The first one is considered canonical for the group implicitly, or they are just tracked
            dup_counter += 1
            
    # Write to CSV
    fieldnames = [
        "source_id", "filename", "relative_path", "file_type", "file_size", "content_hash",
        "source_family", "report_type", "report_date", "reporting_period", "publication_date",
        "revision_information", "historical_current_classification", "duplicate_group", 
        "official_match", "extraction_status", "pages", "tables_detected", "figures_detected",
        "extraction_method", "processing_version", "processing_timestamp", "source_confidence", "notes"
    ]
    
    with open(MANIFEST_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_records)
        
    print(f"Manifest generated at {MANIFEST_PATH} with {len(manifest_records)} records.")

if __name__ == "__main__":
    build_manifest()
