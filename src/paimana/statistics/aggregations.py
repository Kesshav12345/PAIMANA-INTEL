import pandas as pd
from paimana.formulas.registry import compute_cost_overrun_pct, compute_financial_progress

def calculate_portfolio_aggregations(df: pd.DataFrame, group_by_col: str) -> pd.DataFrame:
    """
    Calculates 10/10 semantically correct aggregations.
    Does NOT average percentages. It sums the numerators and denominators.
    """
    if df.empty:
        return pd.DataFrame()
        
    agg = df.groupby(group_by_col).agg({
        'Project_SK': 'count',
        'Original_Cost': 'sum',
        'Revised_Cost': 'sum',
        'Anticipated_Cost': 'sum',
        'Cumulative_Expenditure': 'sum'
    }).rename(columns={'Project_SK': 'Project_Count'})
    
    # Correct Semantic Aggregations
    agg['Aggregate_Cost_Overrun_Pct'] = agg.apply(
        lambda row: compute_cost_overrun_pct(row['Anticipated_Cost'], row['Original_Cost']),
        axis=1
    )
    
    agg['Aggregate_Financial_Progress_Pct'] = agg.apply(
        lambda row: compute_financial_progress(row['Cumulative_Expenditure'], row['Anticipated_Cost']),
        axis=1
    )
    
    return agg.reset_index()
