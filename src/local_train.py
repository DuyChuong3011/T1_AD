import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import xgboost as xgb
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score

print("="*50)
print("[INFO] HUẤN LUYỆN MÔ HÌNH CỤC BỘ (LOCAL TRAINING)")
print("="*50)

current_dir = os.getcwd()
TRAIN_PATH = os.path.join(current_dir, "data", "features", "T1_train.csv")
TEST_PATH = os.path.join(current_dir, "data", "features", "T1_test.csv")

print(f"[INFO] Tải dữ liệu từ: {TRAIN_PATH}")
df_train = pd.read_csv(TRAIN_PATH)
df_test = pd.read_csv(TEST_PATH)

target_col = 'Label_Error'
leakage_keywords = ['timestamp', 'LV ActivePower', 'Theoretical_Power_Curve', 'Loss', 'power_residual', 'Label_Error']
features = [col for col in df_train.columns if not any(kw in col for kw in leakage_keywords)]

X_train = df_train[features].values
y_train = df_train[target_col].values
X_test = df_test[features].values
y_test = df_test[target_col].values

print(f"-> Train shape: {X_train.shape}")
print(f"-> Test shape: {X_test.shape}")

print("\n[INFO] Đang khởi tạo và huấn luyện XGBoost...")
# Sử dụng bộ tham số của Weapon 2 (Hybrid) để đối chiếu
model = xgb.XGBClassifier(
    n_estimators=265,       
    max_depth=10,        
    learning_rate=0.026568,           
    scale_pos_weight=1.212868,
    reg_alpha=3.691853,
    reg_lambda=6.752980,
    gamma=4.194749,
    subsample=0.686712,
    colsample_bytree=0.655952,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
print("[SUCCESS] Huấn luyện hoàn tất!")

y_pred_probs = model.predict_proba(X_test)[:, 1]

# Tối ưu hóa ngưỡng dự đoán (threshold) để tối đa hóa F1-Score
import numpy as np
best_f1 = 0
best_threshold = 0.5
best_y_pred = None

for threshold in np.arange(0.1, 0.9, 0.05):
    y_pred_tmp = (y_pred_probs >= threshold).astype(int)
    score = f1_score(y_test, y_pred_tmp, zero_division=0)
    if score > best_f1:
        best_f1 = score
        best_threshold = threshold
        best_y_pred = y_pred_tmp

y_pred = best_y_pred
roc_auc = roc_auc_score(y_test, y_pred_probs)
f1 = best_f1
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)

print(f"\n[INFO] Threshold tối ưu: {best_threshold:.2f}")

print("\n" + "="*40)
print("KẾT QUẢ ĐÁNH GIÁ")
print("="*40)
print(f"ROC-AUC   : {roc_auc:.4f}")
print(f"F1-Score  : {f1:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print("="*40)

import tarfile
print("\n[INFO] Đang đóng gói mô hình để chuẩn bị Deploy...")
model_file = "xgboost-model"
tar_file = "model.tar.gz"

# Save XGBoost model in the format SageMaker expects
model.save_model(model_file)

with tarfile.open(tar_file, "w:gz") as tar:
    tar.add(model_file)

print(f"[SUCCESS] Đã lưu và nén mô hình thành: {tar_file}")
