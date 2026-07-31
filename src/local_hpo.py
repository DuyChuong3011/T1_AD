import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
import xgboost as xgb
import optuna
from sklearn.metrics import f1_score
from sklearn.model_selection import TimeSeriesSplit

print("="*50)
print("[INFO] BẮT ĐẦU TỐI ƯU HÓA SIÊU THAM SỐ (LOCAL HPO)")
print("="*50)

# Load data
TRAIN_PATH = "data/features/T1_train.csv"
print(f"[INFO] Tải dữ liệu huấn luyện: {TRAIN_PATH}")
df_train = pd.read_csv(TRAIN_PATH)

target_col = 'Label_Error'
leakage_keywords = ['timestamp', 'LV ActivePower', 'Theoretical_Power_Curve', 'Loss', 'power_residual', 'Label_Error']
features = [col for col in df_train.columns if not any(kw in col for kw in leakage_keywords)]

X = df_train[features].values
y = df_train[target_col].values

print(f"-> Tập dữ liệu có {X.shape[0]} mẫu, {X.shape[1]} đặc trưng (Không Leakage)")

# Khởi tạo TimeSeriesSplit để tránh nhìn trộm tương lai
tscv = TimeSeriesSplit(n_splits=3)

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 400),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'scale_pos_weight': trial.suggest_float('scale_pos_weight', 1.0, 30.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 10.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 10.0),
        'gamma': trial.suggest_float('gamma', 0.0, 5.0),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'random_state': 42,
        'n_jobs': -1
    }
    
    cv_scores = []
    
    for train_index, val_index in tscv.split(X):
        X_trn, X_val = X[train_index], X[val_index]
        y_trn, y_val = y[train_index], y[val_index]
        
        model = xgb.XGBClassifier(**params)
        model.fit(X_trn, y_trn)
        
        # Lấy xác suất
        y_pred_probs = model.predict_proba(X_val)[:, 1]
        
        # Tối ưu hóa threshold nhỏ (do dùng scale_pos_weight)
        best_f1 = 0
        for threshold in np.arange(0.3, 0.7, 0.05):
            y_pred = (y_pred_probs >= threshold).astype(int)
            score = f1_score(y_val, y_pred, zero_division=0)
            if score > best_f1:
                best_f1 = score
                
        cv_scores.append(best_f1)
        
    # Trả về trung bình F1-Score trên các nếp gấp thời gian
    return np.mean(cv_scores)

optuna.logging.set_verbosity(optuna.logging.WARNING)
study = optuna.create_study(direction='maximize')
print("[INFO] Đang chạy 30 Trials (sử dụng Cross Validation Thời gian)...")
study.optimize(objective, n_trials=30)

print("\n" + "="*40)
print("🏆 [SUCCESS] HPO HOÀN TẤT!")
print("="*40)
print(f"Best Validation F1-Score: {study.best_value:.4f}")
print("Best Parameters:")
for key, value in study.best_params.items():
    print(f"    {key}={value},")
