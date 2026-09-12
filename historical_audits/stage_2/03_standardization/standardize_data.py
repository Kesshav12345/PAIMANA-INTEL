import os
import json
import re
from pathlib import Path

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
RAW_JSON_DIR = WORKSPACE / "stage_2" / "02_extraction" / "raw_json"
STD_JSON_DIR = WORKSPACE / "stage_2" / "03_standardization" / "standardized_json"

def clean_float(val):
    if not val:
        return None
    val = str(val).strip()
    if val.upper() in ["-", "N.A.", "N.A", "NA", "NOT AVAILABLE"]:
        return None
    val = val.replace(',', '')
    try:
        return float(val)
    except ValueError:
        return None

def extract_qpisr_costs(val):
    # Format: 160.00 (220.00) {220.00}
    # Might have N.A.
    if not val: return None, None, None
    val = str(val).strip()
    
    # Try to extract the three parts using regex
    # Matches a number, optionally followed by (number), optionally followed by {number}
    orig, rev, ant = None, None, None
    
    # We can split by spaces and brackets
    # Actually, let's just use regex to extract everything that looks like a number or N.A.
    parts = re.findall(r'([\d\.,]+|N\.A\.|-)', val.replace(" ", ""))
    if len(parts) >= 1: orig = clean_float(parts[0])
    if len(parts) >= 2: rev = clean_float(parts[1])
    if len(parts) >= 3: ant = clean_float(parts[2])
    
    return orig, rev, ant

def extract_qpisr_dates(val):
    # Format: 6/2024 (01-03-2026) {3/2026}
    if not val: return None, None, None
    val = str(val).strip()
    
    # We just want to grab dates in MM/YYYY or DD-MM-YYYY format
    # Simple split by space / brackets might work better
    parts = re.split(r'[\(\)\{\}\s]+', val)
    parts = [p for p in parts if p.strip() and p.strip() not in ["N.A.", "-", "N.A"]]
    
    orig = parts[0] if len(parts) > 0 else None
    rev = parts[1] if len(parts) > 1 else None
    ant = parts[2] if len(parts) > 2 else None
    
    return orig, rev, ant

def extract_qpisr_name_agency_code(val):
    # Format: HP CRUDE TO OLEFINS (HPCL) (N18000296)
    if not val: return None, None, None
    val = str(val).strip()
    
    name, agency, code = val, None, None
    
    # Try to find (Code) at the end
    match_code = re.search(r'\(([^)]+)\)$', val)
    if match_code:
        code = match_code.group(1).strip()
        val = val[:match_code.start()].strip()
    
    # Try to find (Agency)
    match_agency = re.search(r'\(([^)]+)\)$', val)
    if match_agency:
        agency = match_agency.group(1).strip()
        name = val[:match_agency.start()].strip()
    else:
        name = val
        
    return name, agency, code

def standardize_file(source_id, data):
    report_type = data['source_metadata']['report_type']
    tables = data.get('tables', [])
    
    standardized_records = []
    
    for t in tables:
        headers = [str(h).lower().strip() for h in t.get('headers', []) if h]
        headers_text = " ".join(headers)
        rows = t.get('rows', [])
        
        if "project id" in headers_text and "original cost" in headers_text:
            # FLASH REPORT PROJECT OBSERVATION
            # Find indices
            try:
                # Find best column matches based on substring
                id_col = next(i for i, h in enumerate(t.get('headers', [])) if "project id" in h.lower())
                name_col = next(i for i, h in enumerate(t.get('headers', [])) if "project name" in h.lower())
                orig_col = next(i for i, h in enumerate(t.get('headers', [])) if "original cost" in h.lower())
                rev_col = next(i for i, h in enumerate(t.get('headers', [])) if "revised cost" in h.lower())
                exp_col = next(i for i, h in enumerate(t.get('headers', [])) if "expenditure" in h.lower())
                prog_col = next(i for i, h in enumerate(t.get('headers', [])) if "physical progress" in h.lower())
                
                for row in rows:
                    if len(row) <= max(id_col, name_col, orig_col, rev_col, exp_col, prog_col): continue
                    
                    pid = str(row[id_col]).strip()
                    if not pid or pid.lower() == "project id": continue # Skip header rows mistakenly caught
                    
                    record = {
                        "grain": "PROJECT_OBSERVATION",
                        "source_id": source_id,
                        "report_type": report_type,
                        "paimana_id": pid,
                        "project_code": None,
                        "project_name": str(row[name_col]).strip(),
                        "agency_name": None,
                        "state_name": None,
                        "sector_name": None,
                        "date_of_approval": None,
                        "original_cost": clean_float(row[orig_col]),
                        "revised_cost": clean_float(row[rev_col]),
                        "anticipated_cost": None,
                        "cumulative_expenditure": clean_float(row[exp_col]),
                        "physical_progress_pct": clean_float(row[prog_col]),
                        "original_completion_date": None,
                        "revised_completion_date": None,
                        "anticipated_completion_date": None
                    }
                    standardized_records.append(record)
            except StopIteration:
                pass # Missing a required column
                
        elif "project code" in headers_text and "date of approval" in headers_text:
            # QPISR PROJECT OBSERVATION
            try:
                state_col = next(i for i, h in enumerate(t.get('headers', [])) if "state" in h.lower())
                sec_col = next(i for i, h in enumerate(t.get('headers', [])) if "sector" in h.lower())
                name_col = next(i for i, h in enumerate(t.get('headers', [])) if "project name" in h.lower())
                appr_col = next(i for i, h in enumerate(t.get('headers', [])) if "date of approval" in h.lower())
                date_col = next(i for i, h in enumerate(t.get('headers', [])) if "date of commissioning" in h.lower())
                cost_col = next(i for i, h in enumerate(t.get('headers', [])) if "cost original" in h.lower())
                exp_col = next(i for i, h in enumerate(t.get('headers', [])) if "cumulative expenditure" in h.lower())
                prog_col = next(i for i, h in enumerate(t.get('headers', [])) if "physical progress" in h.lower())
                
                for row in rows:
                    if len(row) <= max(state_col, sec_col, name_col, appr_col, date_col, cost_col, exp_col, prog_col): continue
                    
                    val_name = str(row[name_col]).strip()
                    if not val_name or "Project Name" in val_name: continue
                    
                    name, agency, code = extract_qpisr_name_agency_code(val_name)
                    orig_cost, rev_cost, ant_cost = extract_qpisr_costs(row[cost_col])
                    orig_date, rev_date, ant_date = extract_qpisr_dates(row[date_col])
                    
                    record = {
                        "grain": "PROJECT_OBSERVATION",
                        "source_id": source_id,
                        "report_type": report_type,
                        "paimana_id": None,
                        "project_code": code,
                        "project_name": name,
                        "agency_name": agency,
                        "state_name": str(row[state_col]).strip(),
                        "sector_name": str(row[sec_col]).strip(),
                        "date_of_approval": str(row[appr_col]).strip(),
                        "original_cost": orig_cost,
                        "revised_cost": rev_cost,
                        "anticipated_cost": ant_cost,
                        "cumulative_expenditure": clean_float(row[exp_col]),
                        "physical_progress_pct": clean_float(row[prog_col]),
                        "original_completion_date": orig_date,
                        "revised_completion_date": rev_date,
                        "anticipated_completion_date": ant_date
                    }
                    standardized_records.append(record)
            except StopIteration:
                pass
                
        elif "sector" in headers_text and "achievement" in headers_text:
            # SECTOR PERFORMANCE
            try:
                sec_col = next(i for i, h in enumerate(t.get('headers', [])) if "sector" in h.lower())
                unit_col = next(i for i, h in enumerate(t.get('headers', [])) if "unit" in h.lower())
                
                # Finding achievements can be tricky due to multi-level headers. We will just grab the next columns.
                # Assuming standard layout: Sector | Unit | Achievement | Achievement (Prev Year) | Growth
                # We will just look for keywords in headers
                ach_cols = [i for i, h in enumerate(t.get('headers', [])) if "achievement" in str(h).lower()]
                growth_cols = [i for i, h in enumerate(t.get('headers', [])) if "growth" in str(h).lower()]
                
                ach_col = ach_cols[0] if len(ach_cols) > 0 else -1
                prev_ach_col = ach_cols[1] if len(ach_cols) > 1 else -1
                growth_col = growth_cols[0] if len(growth_cols) > 0 else -1
                
                if ach_col != -1:
                    for row in rows:
                        if len(row) <= max(sec_col, unit_col, ach_col): continue
                        sector = str(row[sec_col]).strip()
                        if not sector or "Sector" in sector: continue
                        
                        record = {
                            "grain": "SECTOR_PERFORMANCE",
                            "source_id": source_id,
                            "report_type": report_type,
                            "metric_name": sector,
                            "metric_unit": str(row[unit_col]).strip(),
                            "achievement_value": clean_float(row[ach_col]),
                            "previous_year_value": clean_float(row[prev_ach_col]) if prev_ach_col != -1 and len(row) > prev_ach_col else None,
                            "growth_pct_yoy": clean_float(row[growth_col]) if growth_col != -1 and len(row) > growth_col else None,
                            "target_value": None,
                            "cumulative_growth_pct": None
                        }
                        standardized_records.append(record)
            except StopIteration:
                pass
                
    return standardized_records

def main():
    if not STD_JSON_DIR.exists():
        STD_JSON_DIR.mkdir(parents=True)
        
    for json_file in RAW_JSON_DIR.glob("*.json"):
        source_id = json_file.stem
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        std_records = standardize_file(source_id, data)
        
        if std_records:
            out_path = STD_JSON_DIR / f"{source_id}_std.json"
            with open(out_path, 'w', encoding='utf-8') as out_f:
                json.dump(std_records, out_f, indent=2)

if __name__ == "__main__":
    main()
