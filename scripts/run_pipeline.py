import subprocess
from pathlib import Path
import sys

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")

def run_step(name, script_path):
    print(f"\n{'='*50}")
    print(f"Executing: {name}")
    print(f"Script: {script_path}")
    print(f"{'='*50}")
    
    result = subprocess.run([sys.executable, str(script_path)], cwd=WORKSPACE)
    if result.returncode != 0:
        print(f"❌ Failed: {name}")
        sys.exit(1)
    else:
        print(f"✅ Success: {name}")

def main():
    print("PAIMANA-INTEL Stage 3 Master Pipeline")
    print("This pipeline rebuilds the canonical database, computes analytics, and generates ML datasets.")
    
    steps = [
        ("1. Canonical DB Build", WORKSPACE / "src" / "database" / "load_sqlite.py"),
        ("2. Compute Analytics", WORKSPACE / "src" / "analytics" / "features.py"),
        ("3. Generate ML Dataset", WORKSPACE / "src" / "ml" / "generate_dataset.py"),
        ("4. Train ML Baseline", WORKSPACE / "src" / "ml" / "train_baseline.py")
    ]
    
    for name, path in steps:
        if path.exists():
            run_step(name, path)
        else:
            print(f"❌ Script not found: {path}")
            sys.exit(1)
            
    print("\n🎉 Pipeline Execution Complete!")

if __name__ == "__main__":
    main()
