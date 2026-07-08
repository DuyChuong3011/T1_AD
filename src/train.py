import argparse
import os
import pandas as pd
import joblib
from sklearn.mixture import GaussianMixture

def main():
    parser = argparse.ArgumentParser()
    # 1. Nhận Hyperparameters từ command line cho GMM
    parser.add_argument('--n_components', type=int, default=5)
    
    # 2. Nhận đường dẫn thư mục Data và Model từ AWS SageMaker (hoặc Local)
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', '../models'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN', '../data/features'))

    args = parser.parse_args()

    # 3. Đọc dữ liệu train
    print(f"[INFO] Đang tìm dữ liệu tại: {args.train}")
    train_path = os.path.join(args.train, "T1_train.csv")
    
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Không tìm thấy file {train_path}")

    df_train = pd.read_csv(train_path)

    # --- FEATURE SELECTION: Chỉ lấy zscore và diff ---
    features = [col for col in df_train.columns if ('zscore' in col) or ('diff' in col)]
    X_train = df_train[features]

    # 4. Huấn luyện mô hình GMM
    print(f"[INFO] Bắt đầu train GMM với {len(features)} features...")
    print(f"[INFO] Tham số: n_components={args.n_components}")

    model = GaussianMixture(
        n_components=args.n_components,
        covariance_type='full',
        random_state=42
    )
    
    model.fit(X_train)
    print("[INFO] Huấn luyện thành công!")

    # 5. Lưu mô hình bằng joblib
    os.makedirs(args.model_dir, exist_ok=True)
    model_path = os.path.join(args.model_dir, "model.joblib")
    joblib.dump(model, model_path)
    print(f"[INFO] Đã lưu model thành công tại: {model_path}")

if __name__ == '__main__':
    main()