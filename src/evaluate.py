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
    
    # Tham số contamination dùng để tính F1-score
    parser.add_argument('--contamination', type=float, default=0.015)
    
    args = parser.parse_args()

    if args.output_dir == '/opt/ml/processing/evaluation':
        args.output_dir = '../reports'

    print("[INFO] Đang tải mô hình GMM và dữ liệu test...")
    # 1. Load model
    model_path = os.path.join(args.model_dir, "model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Không tìm thấy file model tại: {model_path}")
    model = joblib.load(model_path)

    # 2. Load test data
    test_path = os.path.join(args.test, "T1_test.csv")
    df_test = pd.read_csv(test_path)

    # 3. Tạo Pseudo-labels để đánh giá (Quy tắc 3-Sigma: ngưỡng -3.0 của power_residual)
    threshold = -3.0
    y_test_pseudo = (df_test['power_residual'] < threshold).astype(int)

    # --- FEATURE SELECTION ---
    features = [col for col in df_test.columns if ('zscore' in col) or ('diff' in col)]
    X_test = df_test[features]

    print("[INFO] Đang dự đoán và chấm điểm...")
    
    # 4. Lấy điểm log-likelihood từ GMM (Đổi dấu để điểm càng cao càng bất thường)
    anomaly_scores = -model.score_samples(X_test)

    # Tính ngưỡng để phân loại 0/1 dựa trên tỷ lệ contamination giả định
    threshold_gmm = np.percentile(anomaly_scores, 100 * (1 - args.contamination))
    preds_mapped = (anomaly_scores > threshold_gmm).astype(int)

    # 5. Tính toán các chỉ số
    f1 = f1_score(y_test_pseudo, preds_mapped)
    auc = roc_auc_score(y_test_pseudo, anomaly_scores)
    precision = precision_score(y_test_pseudo, preds_mapped, zero_division=0)
    recall = recall_score(y_test_pseudo, preds_mapped)

    print(f"[RESULT] Pseudo AUC-ROC: {auc:.4f} | Pseudo F1: {f1:.4f}")

    # 6. Đóng gói kết quả JSON
    report_dict = {
        "classification_metrics": {
            "pseudo_auc": {"value": auc, "standard_deviation": "NaN"},
            "pseudo_f1": {"value": f1, "standard_deviation": "NaN"},
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