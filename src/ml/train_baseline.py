import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from pathlib import Path

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DATA_PATH = WORKSPACE / "data" / "ml" / "ML_DATASET.csv"

def train_and_evaluate():
    """Train baseline models on the point-in-time safe dataset."""
    if not DATA_PATH.exists():
        print(f"ML dataset not found at {DATA_PATH}")
        return
        
    df = pd.read_csv(DATA_PATH)
    
    # Define feature set and target
    features = [
        'Original_Cost', 
        'Revised_Cost', 
        'Anticipated_Cost', 
        'Cumulative_Expenditure',
        'Financial_Progress_Pct', 
        'Time_Elapsed_Pct', 
        'Schedule_Delay_Months', 
        'Physical_Progress_Pct'
    ]
    
    target = 'Target_Delayed_6M'
    
    # Impute missing with 0 for baseline simplicity
    X = df[features].fillna(0)
    y = df[target]
    
    # Train/Test Split (Ideal is temporal, using random for baseline verification)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    if len(y.unique()) <= 1:
        print(f"Warning: Target '{target}' only contains a single class ({y.unique()[0]}).")
        print("Cannot train a classification model or compute ROC-AUC on a single class.")
        print("This is expected in a small/clean sample dataset where no projects experienced future delay.")
        return
    
    print("=== Random Forest Baseline ===")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_prob_rf = rf.predict_proba(X_test)[:, 1]
    print(classification_report(y_test, y_pred_rf))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob_rf):.3f}\n")
    
    print("=== Logistic Regression Baseline ===")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    y_prob_lr = lr.predict_proba(X_test)[:, 1]
    print(classification_report(y_test, y_pred_lr))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob_lr):.3f}\n")

if __name__ == "__main__":
    train_and_evaluate()
