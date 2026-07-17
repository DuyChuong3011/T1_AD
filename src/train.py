import argparse
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.mixture import GaussianMixture


def model_fn(model_dir):
    model = joblib.load(os.path.join(model_dir, 'model.joblib'))
    return model


def input_fn(request_body, content_type):
    import io
    if content_type == 'text/csv':
        df = pd.read_csv(io.StringIO(request_body))
        return df
    raise ValueError(f"Unsupported content type: {content_type}")


def predict_fn(input_data, model):
    features = [col for col in input_data.columns
                if 'diff' in col]
    X = input_data[features]
    log_likelihood = model.score_samples(X)
    min_ll = -1000
    max_ll = 0
    normalized = (log_likelihood - min_ll) / (max_ll - min_ll)
    fault_prob = 1 - normalized
    fault_prob = float(np.clip(fault_prob, 0, 1)[0])
    return fault_prob


def output_fn(prediction, accept):
    return str(prediction), accept


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_components', type=int, default=5)
    parser.add_argument('--model-dir', type=str,
                        default=os.environ.get('SM_MODEL_DIR', '../models'))
    parser.add_argument('--train', type=str,
                        default=os.environ.get('SM_CHANNEL_TRAIN',
                                               '../data/features'))
    args = parser.parse_args()

    print(f"[INFO] Đang tìm dữ liệu tại: {args.train}")
    train_path = os.path.join(args.train, "T1_train.csv")

    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Không tìm thấy file {train_path}")

    df_train = pd.read_csv(train_path)
    print(f"[INFO] Shape: {df_train.shape}")
    print(f"[INFO] Columns: {list(df_train.columns)}")

    features = [col for col in df_train.columns if 'diff' in col]
    print(f"[INFO] Features dùng train: {features}")
    print(f"[INFO] Số features: {len(features)}")

    X_train = df_train[features]

    print(f"[INFO] Train GMM với {len(features)} features...")
    model = GaussianMixture(
        n_components=args.n_components,
        covariance_type='full',
        random_state=42
    )
    model.fit(X_train)
    print(f"[INFO] Feature names: {list(model.feature_names_in_)}")
    print("[INFO] Train xong!")

    os.makedirs(args.model_dir, exist_ok=True)
    model_path = os.path.join(args.model_dir, "model.joblib")
    joblib.dump(model, model_path)
    print(f"[INFO] Lưu model tại: {model_path}")


if __name__ == '__main__':
    main()