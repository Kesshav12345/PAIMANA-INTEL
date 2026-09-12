import os
import json
import csv
import re
from pathlib import Path

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
STD_JSON_DIR = WORKSPACE / "stage_2" / "03_standardization" / "standardized_json"
IDENTITY_JSON_DIR = WORKSPACE / "stage_2" / "04_identity" / "resolved_json"
IDENTITY_REPORT = WORKSPACE / "stage_2" / "04_identity" / "IDENTITY_RESOLUTION.csv"

def normalize_name(name):
    if not name: return ""
    # Remove extra spaces, lowercase, remove common prefixes/suffixes
    n = str(name).lower()
    n = re.sub(r'[^a-z0-9\s]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def resolve_identities():
    if not IDENTITY_JSON_DIR.exists():
        IDENTITY_JSON_DIR.mkdir(parents=True)
        
    project_registry = {} # normalized_name -> Project_SK
    next_sk = 1
    
    resolution_log = []
    
    for json_file in STD_JSON_DIR.glob("*_std.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
            
        resolved_records = []
        for r in records:
            if r['grain'] == 'PROJECT_OBSERVATION':
                raw_name = r['project_name']
                norm_name = normalize_name(raw_name)
                
                if not norm_name:
                    r['project_sk'] = -1 # Unknown
                else:
                    if norm_name not in project_registry:
                        project_registry[norm_name] = next_sk
                        resolution_log.append({
                            "Project_SK": next_sk,
                            "Normalized_Name": norm_name,
                            "Original_Name_Sample": raw_name,
                            "PAIMANA_ID": r.get('paimana_id'),
                            "Project_Code": r.get('project_code')
                        })
                        next_sk += 1
                        
                    r['project_sk'] = project_registry[norm_name]
                    
            resolved_records.append(r)
            
        out_path = IDENTITY_JSON_DIR / json_file.name
        with open(out_path, 'w', encoding='utf-8') as out_f:
            json.dump(resolved_records, out_f, indent=2)
            
    if resolution_log:
        with open(IDENTITY_REPORT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=resolution_log[0].keys())
            writer.writeheader()
            writer.writerows(resolution_log)
    print(f"Identity resolution complete. {len(project_registry)} unique projects identified.")

if __name__ == "__main__":
    resolve_identities()
