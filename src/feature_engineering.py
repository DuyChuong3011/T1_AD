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

def encode_wind_direction(df: pd.DataFrame, col_name='Wind Direction (°)') -> pd.DataFrame:
    """Encode Wind Direction into Sin and Cos components."""
    df_feat = df.copy()
    if col_name in df_feat.columns:
        df_feat['Wind_Dir_Sin'] = np.sin(df_feat[col_name] * (2 * np.pi / 360))
        df_feat['Wind_Dir_Cos'] = np.cos(df_feat[col_name] * (2 * np.pi / 360))
        df_feat.drop(col_name, axis=1, inplace=True)
    return df_feat

def calculate_loss(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate power loss (Theoretical - Active)."""
    df_feat = df.copy()
    if 'Theoretical_Power_Curve (KWh)' in df_feat.columns and 'LV ActivePower (kW)' in df_feat.columns:
        df_feat['Loss'] = df_feat['Theoretical_Power_Curve (KWh)'] - df_feat['LV ActivePower (kW)']
    return df_feat

def create_labels(df: pd.DataFrame, loss_threshold=0.5) -> pd.DataFrame:
    """Create Label_Error target variable based on physical logic."""
    df_feat = df.copy()
    if 'Loss' not in df_feat.columns:
        df_feat = calculate_loss(df_feat)
        
    if 'Wind Speed (m/s)' in df_feat.columns and 'LV ActivePower (kW)' in df_feat.columns:
        cond1 = (df_feat['Wind Speed (m/s)'] >= 3.5) & (df_feat['LV ActivePower (kW)'] <= 0.1)
        cond2 = (df_feat['Theoretical_Power_Curve (KWh)'] > 0) & (df_feat['Loss'] > loss_threshold * df_feat['Theoretical_Power_Curve (KWh)'])
        df_feat['Label_Error'] = np.where(cond1 | cond2, 1, 0)
    return df_feat

if __name__ == "__main__":
    import sys
    import os

    # SageMaker Processing paths
    input_dir = "/opt/ml/processing/input"
    output_dir = "/opt/ml/processing/output"

    # Fallback for local testing
    if not os.path.exists(input_dir):
        input_dir = "../data/processed"
    if not os.path.exists(output_dir):
        output_dir = "../data/features"

    print(f"[INFO] Đọc dữ liệu từ: {input_dir}")
    if not os.path.exists(input_dir):
        print(f"[ERROR] Không tìm thấy thư mục {input_dir}. Đảm bảo bạn đang đứng ở thư mục 'src' khi chạy code.")
        sys.exit(1)

    # Tìm tất cả file CSV trong input
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

    for input_file in input_files:
        input_path = os.path.join(input_dir, input_file)
        # Giữ đúng tên file hoặc đổi đuôi
        output_file = input_file.replace('.csv', '_features.csv')
        output_path = os.path.join(output_dir, output_file)

        print(f"[INFO] Xử lý: {input_file}")

        # Đọc dữ liệu
        df = pd.read_csv(input_path)

        # Áp dụng feature engineering gốc
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        df = calculate_rolling_stats(df, numeric_cols, windows=[6, 24])
        df = calculate_z_scores(df, numeric_cols)
        df = calculate_differences(df, numeric_cols, periods=[1])
        
        # Áp dụng Hybrid Features (Sin/Cos, Loss, Label)
        df = encode_wind_direction(df)
        df = create_labels(df)

        # Lưu kết quả file tổng
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"[INFO] Đã lưu file tổng: {output_path}")

        # --- TỰ ĐỘNG CHIA TRAIN/TEST ---
        # Import trực tiếp hàm chia của bạn từ preprocessing
        from preprocessing import split_train_test_chrono
        train_df, test_df = split_train_test_chrono(df, test_size=0.3)
        
        train_path = os.path.join(output_dir, 'T1_train_features.csv')
        test_path = os.path.join(output_dir, 'T1_test_features.csv')
        
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        print(f"[INFO] Đã tự động chia tập dữ liệu thành:")
        print(f"       -> {train_path} ({len(train_df)} dòng)")
        print(f"       -> {test_path} ({len(test_df)} dòng)")

    print("[INFO] Hoàn thành toàn bộ Feature Engineering và Split Data!")
