import pandas as pd
import numpy as np


def load_data(path: str, time_col: str = 'Date/Time', freq: str = '10min') -> pd.DataFrame:
    """
    Đọc dữ liệu SCADA T1.csv và đưa về lưới thời gian đều đặn.

    Khác với dữ liệu mô phỏng, dữ liệu thật có các mốc thời gian bị thiếu (gap).
    Hàm parse cột thời gian, sắp xếp, loại trùng, rồi reindex về lưới `freq`
    để các mốc thiếu hiện ra dưới dạng NaN -> bước xử lý missing mới có ý nghĩa.

    Parameters
    ----------
    path : str
        Đường dẫn tới file CSV.
    time_col : str, default 'Date/Time'
        Tên cột thời gian gốc (định dạng '%d %m %Y %H:%M').
    freq : str, default '10min'
        Bước thời gian của lưới.

    Returns
    -------
    pd.DataFrame
        DataFrame có cột 'timestamp' liên tục theo lưới thời gian.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df[time_col] = pd.to_datetime(df[time_col], format='%d %m %Y %H:%M')
    df = df.sort_values(time_col).drop_duplicates(subset=[time_col])

    full_idx = pd.date_range(df[time_col].min(), df[time_col].max(), freq=freq)
    df = df.set_index(time_col).reindex(full_idx)
    df.index.name = 'timestamp'
    df = df.reset_index()
    return df


def handle_missing_values(df: pd.DataFrame, columns=None, strategy='interpolate', fill_value=None) -> pd.DataFrame:
    """
    Xử lý giá trị khuyết trong DataFrame.

    strategy: 'mean' | 'median' | 'mode' | 'constant' | 'ffill' | 'bfill'
              | 'interpolate' (khuyến nghị cho chuỗi thời gian) | 'drop'
    """
    df_clean = df.copy()

    if columns is None:
        columns = df_clean.columns.tolist()
    elif isinstance(columns, str):
        columns = [columns]

    for col in columns:
        if col not in df_clean.columns:
            continue

        if strategy == 'drop':
            df_clean = df_clean.dropna(subset=[col])
        elif strategy == 'ffill':
            df_clean[col] = df_clean[col].ffill()
        elif strategy == 'bfill':
            df_clean[col] = df_clean[col].bfill()
        elif strategy == 'constant':
            if fill_value is not None:
                df_clean[col] = df_clean[col].fillna(fill_value)
            else:
                raise ValueError("fill_value must be provided when strategy='constant'")
        elif strategy == 'mean':
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        elif strategy == 'median':
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        elif strategy == 'mode':
            mode_series = df_clean[col].mode()
            if not mode_series.empty:
                df_clean[col] = df_clean[col].fillna(mode_series.iloc[0])
        elif strategy == 'interpolate':
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].interpolate(method='linear').ffill().bfill()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    return df_clean


def detect_outliers_iqr(df: pd.DataFrame, columns, factor=1.5) -> pd.DataFrame:
    """Phát hiện ngoại lai bằng IQR. Trả về DataFrame boolean (True = ngoại lai)."""
    if isinstance(columns, str):
        columns = [columns]

    outliers_mask = pd.DataFrame(index=df.index)
    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            outliers_mask[col] = False
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        outliers_mask[col] = (df[col] < lower_bound) | (df[col] > upper_bound)

    return outliers_mask


def detect_outliers_zscore(df: pd.DataFrame, columns, threshold=3.0) -> pd.DataFrame:
    """Phát hiện ngoại lai bằng Z-score. Trả về DataFrame boolean (True = ngoại lai)."""
    if isinstance(columns, str):
        columns = [columns]

    outliers_mask = pd.DataFrame(index=df.index)
    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            outliers_mask[col] = False
            continue
        mean_val = df[col].mean()
        std_val = df[col].std()
        if std_val == 0:
            outliers_mask[col] = False
        else:
            z_scores = (df[col] - mean_val) / std_val
            outliers_mask[col] = z_scores.abs() > threshold

    return outliers_mask


def handle_outliers(df: pd.DataFrame, columns=None, method='physical', factor=1.5, threshold=3.0) -> pd.DataFrame:
    """
    Xử lý ngoại lai (Bản Cập nhật Hybrid).
    Thay vì dùng IQR hay Z-score để gọt (gây mất tín hiệu hỏng hóc thực),
    bản nâng cấp này ưu tiên phương pháp 'physical' - chỉ loại bỏ dữ liệu
    phi vật lý (đưa giá trị âm về 0).
    """
    df_clean = df.copy()
    
    # Mặc định clip các cột vật lý về 0
    if method == 'physical':
        if columns is None:
            columns = ['LV ActivePower (kW)', 'Wind Speed (m/s)', 'Theoretical_Power_Curve (KWh)']
        elif isinstance(columns, str):
            columns = [columns]
            
        for col in columns:
            if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].clip(lower=0)
    else:
        # Nếu ai đó gọi lại logic cũ, báo warning
        print("[WARNING] Bạn đang dùng phương pháp IQR/Z-score. Khuyến nghị dùng 'physical' để không mất dữ liệu bất thường.")
        pass # Rút gọn code cũ để đơn giản hóa pipeline XGBoost
        
    return df_clean


def scale_features(df: pd.DataFrame, columns, method='standard', stats=None, return_stats=False):
    """
    Chuẩn hóa đặc trưng số.

    Để tránh rò rỉ dữ liệu: fit trên TRAIN với return_stats=True để lấy tham số,
    sau đó transform TEST bằng cách truyền lại stats đó.

    method: 'standard' (Z-score) | 'minmax' [0,1] | 'robust' (median & IQR).
    """
    df_scaled = df.copy()
    if isinstance(columns, str):
        columns = [columns]

    fitting = stats is None
    if fitting:
        stats = {}

    for col in columns:
        if col not in df_scaled.columns or not pd.api.types.is_numeric_dtype(df_scaled[col]):
            continue

        if method == 'standard':
            if fitting:
                stats[col] = {'mean': df_scaled[col].mean(), 'std': df_scaled[col].std()}
            std_val = stats[col]['std']
            df_scaled[col] = (df_scaled[col] - stats[col]['mean']) / std_val if std_val != 0 else 0.0

        elif method == 'minmax':
            if fitting:
                stats[col] = {'min': df_scaled[col].min(), 'max': df_scaled[col].max()}
            diff_val = stats[col]['max'] - stats[col]['min']
            df_scaled[col] = (df_scaled[col] - stats[col]['min']) / diff_val if diff_val != 0 else 0.0

        elif method == 'robust':
            if fitting:
                stats[col] = {'median': df_scaled[col].median(),
                              'iqr': df_scaled[col].quantile(0.75) - df_scaled[col].quantile(0.25)}
            iqr = stats[col]['iqr']
            df_scaled[col] = (df_scaled[col] - stats[col]['median']) / iqr if iqr != 0 else 0.0
        else:
            raise ValueError(f"Unknown scaling method: {method}")

    if return_stats:
        return df_scaled, stats
    return df_scaled


def split_train_test_chrono(df: pd.DataFrame, test_size=0.3) -> tuple:
    """
    Chia train/test theo thời gian (chronological split) — dùng cho dữ liệu KHÔNG nhãn.

    Phần đầu chuỗi (1 - test_size) làm train, phần cuối làm test. Giữ nguyên thứ tự
    thời gian, không xáo trộn, tránh rò rỉ dữ liệu tương lai vào quá khứ.

    Returns
    -------
    (train_df, test_df)
    """
    df_sorted = df.copy().reset_index(drop=True)
    cut = int(len(df_sorted) * (1 - test_size))
    train_df = df_sorted.iloc[:cut].reset_index(drop=True)
    test_df = df_sorted.iloc[cut:].reset_index(drop=True)
    return train_df, test_df
