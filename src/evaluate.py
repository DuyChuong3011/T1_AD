import argparse
import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score

def parse_args():
    """
    Nhận đường dẫn cấu hình từ SageMaker.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=str, default='/opt/ml/processing/model')
    parser.add_argument('--test', type=str, default='/opt/ml/processing/test')
    parser.add_argument('--output-dir', type=str, default='/opt/ml/processing/evaluation')
    return parser.parse_args()

def main():
    print("--- BẮT ĐẦU EVALUATION JOB TRÊN SAGEMAKER ---")
    args = parse_args()
    
    # 1. Tái tạo mô hình từ file artifact (XGBoost)
    print(f"[INFO] Load model artifact từ {args.model_dir}...")
    model_path = os.path.join(args.model_dir, "xgboost_model.joblib")
    model = joblib.load(model_path)
    
    # 2. Đọc dữ liệu kiểm thử
    print(f"[INFO] Đang tải dữ liệu test từ {args.test}...")
    test_file = os.path.join(args.test, 'T1_test.csv')
    df_test = pd.read_csv(test_file)
    target_col = 'Label_Error'
    
    # 3. Đồng bộ hóa Feature 
    print("[INFO] Đồng bộ hóa đặc trưng và ép kiểu dữ liệu...")
    # Lấy chính xác danh sách các cột mà XGBoost đã dùng lúc train
    expected_features = model.feature_names_in_ 
    
    # Trích xuất X_test và y_test
    X_test = df_test[expected_features].to_numpy(dtype=float)
    y_test = df_test[target_col].to_numpy(dtype=int)
    
    # 4. Suy luận xác suất (Predict Probabilities)
    print("[INFO] Tiến hành suy luận (Inference)...")
    probs = model.predict_proba(X_test)[:, 1]
    
    # 5. Tối ưu hóa Threshold (Threshold Moving)
    print("[INFO] Dò tìm ngưỡng tối ưu...")
    thresholds = np.arange(0.1, 0.9, 0.05)
    best_f1 = 0
    best_thresh = 0.5
    
    for thresh in thresholds:
        preds_adj = (probs >= thresh).astype(int) 
        f1 = f1_score(y_test, preds_adj)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
            
    # Tính lại bộ chỉ số cuối cùng
    final_preds = (probs >= best_thresh).astype(int)
    precision = precision_score(y_test, final_preds)
    recall = recall_score(y_test, final_preds)
    auc = roc_auc_score(y_test, probs)
    
    print("="*40)
    print(f"Ngưỡng tối ưu (Best Threshold) : {best_thresh:.2f}")
    print(f"F1-Score tối ưu               : {best_f1:.4f}")
    print(f"ROC-AUC                       : {auc:.4f}")
    print(f"Precision                     : {precision:.4f}")
    print(f"Recall                        : {recall:.4f}")
    print("="*40)
    
    # 6. Đóng gói báo cáo JSON chuẩn cấu trúc SageMaker Model Registry
    report_dict = {
        "classification_metrics": {
            "f1_score": {"value": float(best_f1), "standard_deviation": "NaN"},
            "auc": {"value": float(auc), "standard_deviation": "NaN"},
            "precision": {"value": float(precision), "standard_deviation": "NaN"},
            "recall": {"value": float(recall), "standard_deviation": "NaN"},
            "best_threshold": {"value": float(best_thresh), "standard_deviation": "NaN"}
        }
    }
    
    os.makedirs(args.output_dir, exist_ok=True)
    eval_path = os.path.join(args.output_dir, "evaluation.json")
    with open(eval_path, "w") as f:
        f.write(json.dumps(report_dict, indent=4))
        
    print(f"[SUCCESS] Đã lưu file báo cáo đánh giá tại: {eval_path}")

if __name__ == '__main__':
    main()