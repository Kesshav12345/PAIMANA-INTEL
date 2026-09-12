import sqlite3
import pandas as pd
from pathlib import Path

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "stage_2" / "05_canonical" / "paimana_analytical.db"
WPI_PATH = WORKSPACE / "Secondary dataset" / "WPI and PPIs" / "wpi_monthly_index_202608.xlsx"

def integrate_wpi():
    if not WPI_PATH.exists():
        print("WPI Data file not found.")
        return
        
    try:
        # Assuming the WPI data has standard tabular layout. We will just load the first sheet.
        df_wpi = pd.read_excel(WPI_PATH)
        
        # Clean column names (strip spaces, replace spaces with underscores)
        df_wpi.columns = [str(c).strip().replace(' ', '_').replace('.', '') for c in df_wpi.columns]
        
        conn = sqlite3.connect(DB_PATH)
        df_wpi.to_sql("Dim_WPI", conn, if_exists="replace", index=False)
        
        # We could also write a crosswalk here, but for simplicity, the table is now in SQLite
        # downstream analytical views can JOIN Fact_Project_Observation with Dim_WPI on Month/Year.
        
        conn.close()
        print(f"WPI data integrated. Table Dim_WPI created with {len(df_wpi)} rows.")
    except Exception as e:
        print(f"Failed to integrate WPI data: {e}")

if __name__ == "__main__":
    integrate_wpi()
