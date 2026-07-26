import argparse
import os
import pandas as pd
import xgboost as xgb
import joblib
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score, classification_report

def parse_args():
    """
    Nhận hyperparameters và đường dẫn từ command line do SageMaker truyền vào.
    """
    parser = argparse.ArgumentParser()
    
    # 1. Các tham số hệ thống mặc định của SageMaker (Environment Variables)
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', './model'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN', './data/train'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST', './data/test'))
    
    # 2. Hyperparameters cho XGBoost
    parser.add_argument('--n_estimators', type=int, default=150)
    parser.add_argument('--max_depth', type=int, default=6)
    parser.add_argument('--learning_rate', type=float, default=0.1)
    parser.add_argument('--scale_pos_weight', type=float, default=1.0)
    
    return parser.parse_args()

def load_data(train_path, test_path):
    """
    Đọc dữ liệu CSV từ thư mục mounted của SageMaker và tách X, y.
    """
    print(f"[INFO] Đang tải dữ liệu từ {train_path} và {test_path}...")
    
    train_file = os.path.join(train_path, 'T1_train.csv')
    test_file = os.path.join(test_path, 'T1_test.csv')
    
    df_train = pd.read_csv(train_file)
    df_test = pd.read_csv(test_file)
    
    target_col = 'Label_Error'
    
    # Đảm bảo không có data leakage (chặn biến power_residual như đã phân tích)
    leakage_keywords = ['timestamp', 'LV ActivePower', 'Theoretical_Power_Curve', 'Loss', 'power_residual', 'Label_Error']
    features = [col for col in df_train.columns if not any(kw in col for kw in leakage_keywords)]
    
    X_train = df_train[features]
    y_train = df_train[target_col].values
    X_test = df_test[features]
    y_test = df_test[target_col].values
    
    return X_train, y_train, X_test, y_test

def build_model(args):
    """
    Khởi tạo mô hình XGBoost với các hyperparameters từ đối số.
    """
    print("[INFO] Khởi tạo kiến trúc XGBoost...")
    model = xgb.XGBClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        scale_pos_weight=args.scale_pos_weight,
        random_state=42,
        n_jobs=-1
    )
    return model

def train(model, X_train, y_train, X_test, y_test):
    """
    Huấn luyện mô hình, có thể cấu hình thêm early stopping nếu cần.
    """
    print("[INFO] Bắt đầu quá trình huấn luyện...")
    model.fit(
        X_train, 
        y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=10
    )
    return model

def evaluate(model, X_test, y_test):
    """
    Đánh giá nhanh trên luồng training.
    """
    print("[INFO] Tiến hành đánh giá nhanh mô hình...")
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    f1 = f1_score(y_test, preds)
    auc = roc_auc_score(y_test, probs)
    precision = precision_score(y_test, preds)
    recall = recall_score(y_test, preds)
    
    print("="*40)
    print(f"ROC-AUC   : {auc:.4f}")
    print(f"Validation-F1: {f1:.4f}") 
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print("="*40)

def save_model(model, model_dir):
    """
    Lưu model artifact ra đúng thư mục để SageMaker tự động nén thành model.tar.gz.
    """
    print(f"[INFO] Lưu mô hình tại đường dẫn: {model_dir}")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "xgboost_model.joblib")
    joblib.dump(model, model_path)
    print("[SUCCESS] Đã lưu mô hình thành công.")

def main():
    print("--- BẮT ĐẦU TRAINING JOB TRÊN SAGEMAKER ---")
    args = parse_args()
    
    # 1. Load Data
    X_train, y_train, X_test, y_test = load_data(args.train, args.test)
    
    # 2. Build Model
    model = build_model(args)
    
    # 3. Train
    trained_model = train(model, X_train, y_train, X_test, y_test)
    
    # 4. Evaluate (Quick check) 
    evaluate(trained_model, X_test, y_test)
    
    # 5. Save Model
    save_model(trained_model, args.model_dir)

if __name__ == '__main__':
    main()