import os
from pathlib import Path

# The absolute root of the repository, determined dynamically
# config.py is in src/paimana/, so parent.parent.parent is the root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_DIR = REPO_ROOT / "data"
CANONICAL_DB_PATH = DATA_DIR / "canonical" / "paimana_analytical.db"
ML_DATASET_PATH = DATA_DIR / "ml" / "ML_DATASET.csv"

# Historical Audit Data (Stage 2)
STAGE_2_IDENTITY_JSON_DIR = REPO_ROOT / "historical_audits" / "stage_2" / "04_identity" / "resolved_json"
STAGE_2_MANIFEST_PATH = REPO_ROOT / "historical_audits" / "stage_2" / "01_raw" / "SOURCE_MANIFEST.csv"
STAGE_2_IDENTITY_REPORT = REPO_ROOT / "historical_audits" / "stage_2" / "04_identity" / "IDENTITY_RESOLUTION.csv"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CANONICAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
ML_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)

# Settings
ENV = os.getenv("PAIMANA_ENV", "development")
