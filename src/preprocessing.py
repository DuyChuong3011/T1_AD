import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from feature_engineering import transform_wind_direction, extract_time_features, create_error_label

def load_data(path: str, time_col: str = 'Date/Time', freq: str = '10min') -> pd.DataFrame:
    """Đọc dữ liệu SCADA và đưa về lưới thời gian đều đặn (để lộ ra các mốc bị thiếu)."""
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df[time_col] = pd.to_datetime(df[time_col], format='%d %m %Y %H:%M')
    df = df.sort_values(time_col).drop_duplicates(subset=[time_col])

    full_idx = pd.date_range(df[time_col].min(), df[time_col].max(), freq=freq)
    df = df.set_index(time_col).reindex(full_idx)
    df.index.name = 'timestamp'
    df = df.reset_index()
    return df

def clean_physical_noise(df: pd.DataFrame) -> pd.DataFrame:
    """Xử lý nhiễu vật lý cơ bản: Đưa các giá trị âm vô lý về 0."""
    df_clean = df.copy()
    cols_to_check = ['LV ActivePower (kW)', 'Wind Speed (m/s)', 'Theoretical_Power_Curve (KWh)']
    for col in cols_to_check:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(lambda x: max(0.0, x) if pd.notnull(x) else x)
    return df_clean

# Alias cho clean_physical_noise
clean_physical_limits = clean_physical_noise

def encode_wind_direction(df: pd.DataFrame, col: str = 'Wind Direction (°)') -> pd.DataFrame:
    """Mã hóa hướng gió dạng lượng giác."""
    return transform_wind_direction(df, col=col)

def create_labels(df: pd.DataFrame, loss_threshold: float = 0.5) -> pd.DataFrame:
    """Tạo nhãn lỗi và đặc trưng hao hụt công suất."""
    return create_error_label(df)

def handle_missing_values(df: pd.DataFrame, columns=None, strategy='interpolate') -> pd.DataFrame:
    """Nội suy tuyến tính cho các điểm dữ liệu bị khuyết."""
    df_clean = df.copy()
    target_cols = columns if columns is not None else df_clean.select_dtypes(include=[np.number]).columns
    for col in target_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].interpolate(method='linear').ffill().bfill()
    return df_clean

def split_train_test_chrono(df: pd.DataFrame, test_size=0.3) -> tuple:
    """Chia tập Train/Test theo thời gian để tránh rò rỉ dữ liệu tương lai."""
    df_sorted = df.copy().reset_index(drop=True)
    cut = int(len(df_sorted) * (1 - test_size))
    train_df = df_sorted.iloc[:cut].reset_index(drop=True)
    test_df = df_sorted.iloc[cut:].reset_index(drop=True)
    return train_df, test_df

def scale_features(*args, columns=None, method='standard', return_stats=False, stats=None) -> tuple:
    """
    Chuẩn hóa đặc trưng. Hỗ trợ cả 2 dạng gọi:
    1) scale_features(train_df, test_df, columns) -> (train_scaled, test_scaled)
    2) scale_features(df, columns=cols, method='standard', return_stats=True/False, stats=stats)
    """
    
    protected_cols = ['timestamp', 'Label_Error']
    
    if len(args) == 2 and isinstance(args[1], pd.DataFrame):
        train_df, test_df = args[0], args[1]
        
        cols = columns if columns is not None else [
            c for c in train_df.select_dtypes(include=[np.number]).columns 
            if c not in protected_cols
        ]
        
        scaler = MinMaxScaler()
        train_scaled = train_df.copy()
        test_scaled = test_df.copy()
        train_scaled[cols] = scaler.fit_transform(train_scaled[cols])
        test_scaled[cols] = scaler.transform(test_scaled[cols])
        return train_scaled, test_scaled
    
    df = args[0].copy()
    
    cols = columns if columns is not None else [
        c for c in df.select_dtypes(include=[np.number]).columns 
        if c not in protected_cols
    ]
    
    if stats is None:
        if method == 'standard':
            means = df[cols].mean()
            stds = df[cols].std().replace(0, 1.0)
            stats = {'mean': means, 'std': stds}
        else:
            mins = df[cols].min()
            maxs = df[cols].max()
            stats = {'min': mins, 'max': maxs}
            
    if 'mean' in stats:
        df[cols] = (df[cols] - stats['mean']) / stats['std']
    elif 'min' in stats:
        denom = (stats['max'] - stats['min']).replace(0, 1.0)
        df[cols] = (df[cols] - stats['min']) / denom
        
    if return_stats:
        return df, stats
    return df

