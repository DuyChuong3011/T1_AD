import argparse
import os
import pandas as pd
import joblib
import xgboost as xgb

def main():
    parser = argparse.ArgumentParser()
    # Các tham số cơ bản cho mô hình XGBoost
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=6)
    parser.add_argument('--learning_rate', type=float, default=0.1)
    
    # Nhận đường dẫn thư mục Data và Model
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', '../models'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN', '../data/features'))

    args = parser.parse_args()

    # 1. Đọc dữ liệu train
    print(f"[INFO] Đang tìm dữ liệu tại: {args.train}")
    train_path = os.path.join(args.train, "T1_train.csv")
    
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Không tìm thấy file {train_path}")

    df_train = pd.read_csv(train_path)

    # 2. FEATURE SELECTION: Lấy tất cả các cột đặc trưng hữu ích
    # Loại bỏ các cột không phải đặc trưng (như Date/Time, index) và cột Target
    exclude_cols = ['Date/Time', 'timestamp', 'Label_Error', 'index', 'Unnamed: 0']
    features = [col for col in df_train.columns if col not in exclude_cols]
    
    if 'Label_Error' not in df_train.columns:
        raise ValueError("Không tìm thấy cột 'Label_Error' trong dữ liệu train. Vui lòng chạy lại Feature Engineering.")

    X_train = df_train[features]
    y_train = df_train['Label_Error']

    # 3. Huấn luyện mô hình XGBoost
    print(f"[INFO] Bắt đầu train XGBoost với {len(features)} features...")
    print(f"       Features: {features[:5]}...")
    
    model = xgb.XGBClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    print("[INFO] Huấn luyện thành công!")

    # 4. Lưu mô hình bằng joblib
    os.makedirs(args.model_dir, exist_ok=True)
    model_path = os.path.join(args.model_dir, "model.joblib")
    joblib.dump(model, model_path)
    print(f"[INFO] Đã lưu model XGBoost thành công tại: {model_path}")

if __name__ == '__main__':
    main()