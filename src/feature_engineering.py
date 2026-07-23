import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np

def extract_time_features(df: pd.DataFrame, time_col: str = 'timestamp') -> pd.DataFrame:
    """Trích xuất đặc trưng thời gian (Tháng, Giờ) để bắt tính mùa vụ."""
    df_feat = df.copy()
    if time_col in df_feat.columns:
        df_feat['Month'] = df_feat[time_col].dt.month
        df_feat['Hour'] = df_feat[time_col].dt.hour
    return df_feat

def transform_wind_direction(df: pd.DataFrame, col: str = 'Wind Direction (°)') -> pd.DataFrame:
    """Mã hóa Hướng gió (0-360) sang tọa độ lượng giác (Sin/Cos) để giữ tính chu kỳ."""
    df_feat = df.copy()
    if col in df_feat.columns:
        df_feat['Wind_Dir_Sin'] = np.sin(df_feat[col] * (2 * np.pi / 360))
        df_feat['Wind_Dir_Cos'] = np.cos(df_feat[col] * (2 * np.pi / 360))
        df_feat = df_feat.drop(columns=[col])
    return df_feat

def create_error_label(df: pd.DataFrame, loss_threshold: float = 0.5) -> pd.DataFrame:
    """
    Tự động tạo Nhãn Lỗi (Label_Error = 1) dựa trên lý thuyết vật lý.
    Lỗi khi: 
    - Gió đủ lớn (>3.5) nhưng công suất máy ~ 0.
    - Hoặc công suất thực tế hao hụt > 20% so với đường cong lý thuyết.
    """
    df_feat = df.copy()
    
    if all(c in df_feat.columns for c in ['LV ActivePower (kW)', 'Wind Speed (m/s)', 'Theoretical_Power_Curve (KWh)']):
        df_feat['Loss'] = df_feat['Theoretical_Power_Curve (KWh)'] - df_feat['LV ActivePower (kW)']
        
        cond1 = (df_feat['Wind Speed (m/s)'] >= 3.5) & (df_feat['LV ActivePower (kW)'] <= 0.1)
        cond2 = (df_feat['Theoretical_Power_Curve (KWh)'] > 0) & (df_feat['Loss'] > loss_threshold * df_feat['Theoretical_Power_Curve (KWh)'])
        
        df_feat['Label_Error'] = np.where(cond1 | cond2, 1, 0)
    return df_feat

def calculate_lag_features(df: pd.DataFrame, columns, periods=[1]) -> pd.DataFrame:
    """Tạo biến trễ (Lag) cơ bản để mô hình ghi nhớ trạng thái quá khứ (ví dụ: công suất 10 phút trước)."""
    df_feat = df.copy()
    if isinstance(columns, str):
        columns = [columns]
        
    for col in columns:
        if col in df_feat.columns:
            for p in periods:
                df_feat[f"{col}_Lag_{p}"] = df_feat[col].shift(p)
                
    df_feat = df_feat.bfill()
    return df_feat

def calculate_rolling_stats(df: pd.DataFrame, columns, windows=[6, 24]) -> pd.DataFrame:
    """Tính các chỉ số rolling mean và rolling std cho các cột chỉ định."""
    df_feat = df.copy()
    if isinstance(columns, str):
        columns = [columns]
        
    for col in columns:
        if col in df_feat.columns:
            for w in windows:
                df_feat[f"{col}_roll_mean_{w}"] = df_feat[col].rolling(w, min_periods=1).mean()
                df_feat[f"{col}_roll_std_{w}"] = df_feat[col].rolling(w, min_periods=1).std().fillna(0)
    return df_feat

def calculate_z_scores(df: pd.DataFrame, columns) -> pd.DataFrame:
    """Tính điểm Z-score cho các cột chỉ định."""
    df_feat = df.copy()
    if isinstance(columns, str):
        columns = [columns]
        
    for col in columns:
        if col in df_feat.columns:
            mean = df_feat[col].mean()
            std = df_feat[col].std()
            std = std if std != 0 else 1.0
            df_feat[f"{col}_zscore"] = (df_feat[col] - mean) / std
    return df_feat

def calculate_differences(df: pd.DataFrame, columns, periods=[1]) -> pd.DataFrame:
    """Tính sai phân (difference) cho các cột chỉ định."""
    df_feat = df.copy()
    if isinstance(columns, str):
        columns = [columns]
        
    for col in columns:
        if col in df_feat.columns:
            for p in periods:
                df_feat[f"{col}_diff_{p}"] = df_feat[col].diff(p).bfill()
                df_feat[f"{col}_diff"] = df_feat[f"{col}_diff_{p}"]
    return df_feat

