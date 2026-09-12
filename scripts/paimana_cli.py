import sys
from pathlib import Path
import argparse

# Add src to pythonpath
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / "src"))

from paimana.database.schema import init_db
from paimana.ml.generator import generate_ml_dataset
from paimana.ml.baseline import train_baseline

def main():
    parser = argparse.ArgumentParser(description="PAIMANA-INTEL Master CLI")
    parser.add_argument("command", choices=["db-build", "ml-dataset", "train-baseline", "all"], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command in ("db-build", "all"):
        print("--- Rebuilding Canonical DB Schema ---")
        init_db()
        
    if args.command in ("ml-dataset", "all"):
        print("--- Generating ML Dataset ---")
        generate_ml_dataset()
        
    if args.command in ("train-baseline", "all"):
        print("--- Training Baseline Models ---")
        train_baseline()
        
if __name__ == "__main__":
    main()
