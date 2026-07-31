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
features = [c for c in df_train.columns if c not in ['timestamp', target_col]]

X_train = df_train[features].values
y_train = df_train[target_col].values
X_test = df_test[features].values
y_test = df_test[target_col].values

print(f"-> Train shape: {X_train.shape}")
print(f"-> Test shape: {X_test.shape}")

print("\n[INFO] Đang khởi tạo và huấn luyện XGBoost...")
# Sử dụng bộ tham số của Weapon 2 (Hybrid) để đối chiếu
model = xgb.XGBClassifier(
    n_estimators=161,       
    max_depth=3,        
    learning_rate=0.09,           
    scale_pos_weight=10,
    reg_alpha=0.0,
    reg_lambda=0.47,
    gamma=0.42,
    subsample=0.98,
    colsample_bytree=0.66,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
print("[SUCCESS] Huấn luyện hoàn tất!")

# Đánh giá với ngưỡng mặc định 0.5
y_pred_probs = model.predict_proba(X_test)[:, 1]
y_pred = (y_pred_probs >= 0.5).astype(int)

roc_auc = roc_auc_score(y_test, y_pred_probs)
f1 = f1_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)

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
