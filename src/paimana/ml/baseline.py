import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

from paimana.config import ML_DATASET_PATH

def train_baseline():
    if not ML_DATASET_PATH.exists():
        print("ML Dataset not found. Run generator first.")
        return
        
    df = pd.read_csv(ML_DATASET_PATH)
    
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
        
    # Rule 25: Temporal ML Evaluation (No Random Splits!)
    df = df.sort_values(by='Report_Date')
    
    # Simple Temporal Split (first 70% of time is train, last 30% is test)
    split_idx = int(len(df) * 0.7)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    X_train = train_df[features].fillna(0)
    y_train = train_df[target]
    X_test = test_df[features].fillna(0)
    y_test = test_df[target]
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]
    
    print("=== Baseline Model: Random Forest ===")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.3f}")

if __name__ == "__main__":
    train_baseline()
