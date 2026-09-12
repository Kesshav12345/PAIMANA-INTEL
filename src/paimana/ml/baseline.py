import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DATA_PATH = WORKSPACE / "data" / "ml" / "ML_DATASET.csv"

def train_baseline():
    if not DATA_PATH.exists():
        print("ML Dataset not found. Run generator first.")
        return
        
    df = pd.read_csv(DATA_PATH)
    
    features = [
        'Original_Cost', 'Revised_Cost', 'Cumulative_Expenditure',
        'Physical_Progress_Pct', 'Financial_Progress_Pct', 'Physical_Financial_Divergence'
    ]
    target = 'Target_Delayed_Future'
    
    X = df[features].fillna(0)
    y = df[target]
    
    if len(y.unique()) <= 1:
        print(f"Cannot evaluate: Target only has one class ({y.unique()[0]}).")
        return
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]
    
    print("=== Baseline Model: Random Forest ===")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.3f}")

if __name__ == "__main__":
    train_baseline()
