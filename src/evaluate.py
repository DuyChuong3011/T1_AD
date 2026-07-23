import os
import json
import argparse
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score

def main():
    parser = argparse.ArgumentParser()
    # Nhận đường dẫn từ SageMaker hoặc Local
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', '../models'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST', '../data/features'))
    parser.add_argument('--output-dir', type=str, default='/opt/ml/processing/evaluation')
    
    args = parser.parse_args()

    if args.output_dir == '/opt/ml/processing/evaluation':
        args.output_dir = '../reports'

    print("[INFO] Đang tải mô hình XGBoost và dữ liệu test...")
    # 1. Load model
    model_path = os.path.join(args.model_dir, "model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Không tìm thấy file model tại: {model_path}. Đảm bảo bạn đang đứng ở thư mục 'src'.")
    model = joblib.load(model_path)

    # 2. Load test data
    test_path = os.path.join(args.test, "T1_test_features.csv")
    if not os.path.exists(test_path):
        test_path = os.path.join(args.test, "T1_test.csv")

    df_test = pd.read_csv(test_path)
    
    if 'Label_Error' not in df_test.columns:
        raise ValueError("Không tìm thấy cột 'Label_Error' trong dữ liệu test.")

    # 3. Trích xuất đặc trưng và Ground Truth
    exclude_cols = ['Date/Time', 'timestamp', 'Label_Error', 'index', 'Unnamed: 0']
    features = [col for col in df_test.columns if col not in exclude_cols]
    
    X_test = df_test[features]
    y_test_true = df_test['Label_Error']

    print("[INFO] Đang dự đoán và chấm điểm...")
    
    # 4. Lấy điểm dự đoán từ XGBoost
    preds = model.predict(X_test)
    preds_proba = model.predict_proba(X_test)[:, 1]

    # 5. Tính toán các chỉ số
    f1 = f1_score(y_test_true, preds)
    auc = roc_auc_score(y_test_true, preds_proba)
    precision = precision_score(y_test_true, preds, zero_division=0)
    recall = recall_score(y_test_true, preds)

    print(f"[RESULT] True AUC-ROC: {auc:.4f} | True F1: {f1:.4f}")
    print(f"[RESULT] Precision: {precision:.4f} | Recall: {recall:.4f}")

    # 6. Đóng gói kết quả JSON
    report_dict = {
        "classification_metrics": {
            "auc": {"value": auc, "standard_deviation": "NaN"},
            "f1": {"value": f1, "standard_deviation": "NaN"},
            "precision": {"value": precision},
            "recall": {"value": recall}
        }
    }

    # 7. Lưu file JSON
    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "evaluation.json")
    
    with open(out_path, "w") as f:
        f.write(json.dumps(report_dict, indent=4))

    print(f"[INFO] Đã lưu báo cáo đánh giá tại: {out_path}")

if __name__ == '__main__':
    main()