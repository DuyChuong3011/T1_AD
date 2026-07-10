import argparse
import sagemaker
from sagemaker.sklearn.estimator import SKLearn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', type=str, default='scada-fault-prediction')
    parser.add_argument('--role', type=str, default='arn:aws:s3:::scada-fault-prediction')
    args = parser.parse_args()

    print("🚀 Khởi động SageMaker Training Job cho mô hình GMM...")

    # 1. Khởi tạo SKLearn Estimator
    # Báo cho AWS biết ta cần 1 máy ảo loại 'ml.m5.large', chạy môi trường Scikit-Learn
    sklearn_estimator = SKLearn(
        entry_point='src/train.py',             # Script mà máy chủ AWS sẽ chạy
        role=args.role,                         # Quyền truy cập
        instance_count=1,                       # Số lượng máy chủ
        instance_type='ml.m5.large',            # Cấu hình máy (2 vCPU, 8GB RAM)
        framework_version='1.2-1',              # Phiên bản Scikit-learn trên AWS
        base_job_name='wind-turbine-gmm',       # Tiền tố tên Job để dễ quản lý
        hyperparameters={
            'n_components': '5'                   # Truyền tham số cho file train.py
        }
    )

    # 2. Định nghĩa đường dẫn dữ liệu trên S3
    s3_train_data = f's3://{args.bucket}/features'

    # 3. Kích hoạt quá trình huấn luyện trên Cloud
    print(f"[INFO] Đang đẩy code lên AWS và nạp dữ liệu từ: {s3_train_data}")
    
    # Hàm fit() sẽ block màn hình Terminal của em để in log trực tiếp từ máy chủ AWS
    sklearn_estimator.fit({'train': s3_train_data})

    print("\n✅ Training Job đã hoàn tất trên AWS!")
    print(f"📦 Model Artifact được lưu trữ an toàn tại: {sklearn_estimator.model_data}")

if __name__ == '__main__':
    main()
