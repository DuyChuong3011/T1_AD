import argparse
import sagemaker
from sagemaker.sklearn.estimator import SKLearn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', type=str,
                        default='scada-fault-prediction')
    parser.add_argument('--role', type=str,
                        default='arn:aws:iam::036071344072:role/SageMakerExecutionRole-MLOps')
    args = parser.parse_args()

    print("Khởi động SageMaker Training Job...")

    sklearn_estimator = SKLearn(
        entry_point='src/train.py',
        role=args.role,
        instance_count=1,
        instance_type='ml.m5.large',
        framework_version='1.2-1',
        base_job_name='scada-gmm',
        hyperparameters={
            'n_components': '5'
        }
    )

    s3_train_data = f's3://{args.bucket}/features'
    print(f"[INFO] Nạp dữ liệu từ: {s3_train_data}")

    sklearn_estimator.fit({'train': s3_train_data})

    print("Training Job hoàn tất!")
    print(f"Model tại: {sklearn_estimator.model_data}")


if __name__ == '__main__':
    main()