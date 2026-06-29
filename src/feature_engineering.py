import pandas as pd
import numpy as np

def calculate_rolling_stats(df: pd.DataFrame, columns, windows=[3, 6, 12, 24], min_periods=1) -> pd.DataFrame:
    """
    Calculate rolling mean and rolling standard deviation for specified columns.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The input DataFrame.
    columns : list or str
        The column(s) to compute rolling statistics for.
    windows : list of int, default [3, 6, 12, 24]
        The size of the rolling window (in number of observations).
    min_periods : int, default 1
        Minimum number of observations in window required to have a value.
        Setting to 1 avoids generating NaNs at the beginning of the series.
        
    Returns:
    --------
    pd.DataFrame
        A new DataFrame containing the original columns plus the newly created rolling mean/std columns.
    """
    df_feat = df.copy()
    
    if isinstance(columns, str):
        columns = [columns]
        
    for col in columns:
        if col not in df_feat.columns:
            continue
            
        for w in windows:
            # Rolling mean
            mean_col_name = f"{col}_roll_mean_{w}"
            df_feat[mean_col_name] = df_feat[col].rolling(window=w, min_periods=min_periods).mean()
            
            # Rolling standard deviation
            std_col_name = f"{col}_roll_std_{w}"
            df_feat[std_col_name] = df_feat[col].rolling(window=w, min_periods=min_periods).std()
            
            # Fill any remaining NaNs (e.g. standard deviation for window of size 1 with min_periods=1 is NaN)
            df_feat[std_col_name] = df_feat[std_col_name].fillna(0.0)
            
    return df_feat

def calculate_z_scores(df: pd.DataFrame, columns) -> pd.DataFrame:
    """
    Calculate Z-scores for specified columns and return them as new features.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The input DataFrame.
    columns : list or str
        The column(s) to compute Z-scores for.
        
    Returns:
    --------
    pd.DataFrame
        A new DataFrame containing the original columns plus the newly created z-score columns,
        named '{column}_zscore'.
    """
    df_feat = df.copy()
    
    if isinstance(columns, str):
        columns = [columns]
        
    for col in columns:
        if col not in df_feat.columns:
            continue
            
        mean_val = df_feat[col].mean()
        std_val = df_feat[col].std()
        
        z_col_name = f"{col}_zscore"
        if std_val != 0:
            df_feat[z_col_name] = (df_feat[col] - mean_val) / std_val
        else:
            df_feat[z_col_name] = 0.0
            
    return df_feat

def calculate_differences(df: pd.DataFrame, columns, periods=[1]) -> pd.DataFrame:
    """
    Calculate differences (lag differences) for specified columns and return them as new features.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The input DataFrame.
    columns : list or str
        The column(s) to compute differences for.
    periods : list of int, default [1]
        Periods to shift for calculating difference.
        
    Returns:
    --------
    pd.DataFrame
        A new DataFrame containing the original columns plus the newly created difference columns,
        named '{column}_diff_{period}'.
    """
    df_feat = df.copy()
    
    if isinstance(columns, str):
        columns = [columns]
        
    for col in columns:
        if col not in df_feat.columns:
            continue
            
        for p in periods:
            diff_col_name = f"{col}_diff_{p}"
            df_feat[diff_col_name] = df_feat[col].diff(periods=p)
            
            # Fill the initial NaNs created by differencing with 0.0
            df_feat[diff_col_name] = df_feat[diff_col_name].fillna(0.0)
            
    return df_feat
