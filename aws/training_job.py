import sys
sys.stdout.reconfigure(encoding='utf-8')
import sagemaker
from sagemaker.xgboost.estimator import XGBoost
import boto3

def run_training_job():
    print("[INFO] Khởi tạo phiên làm việc với AWS SageMaker...")
    sagemaker_session = sagemaker.Session()
    role = "arn:aws:iam::795644302727:role/SageMakerExecutionRole-MLOps"
    bucket = "amznce23"
    
    # Định nghĩa đường dẫn dữ liệu Tuabin gió trên S3
    train_data_uri = f's3://{bucket}/features/T1_train.csv'
    val_data_uri = f's3://{bucket}/features/T1_test.csv'
    output_path = f's3://{bucket}/models/'

    print("[INFO] Khởi tạo XGBoost Estimator...")
    xgb_estimator = XGBoost(
        entry_point='train.py', 
        source_dir='src', 
        framework_version='1.7-1',
        hyperparameters={
            "num_round": 52,       
            "max_depth": 3,        
            "eta": 0.14,           
            "scale_pos_weight": 10,
            "alpha": 6.27,
            "lambda": 6.30,
            "gamma": 2.12,
            "subsample": 0.93,
            "colsample_bytree": 0.51
        }, 
        role=role,
        instance_count=1,
        instance_type='ml.m5.large',
        output_path=output_path,
        sagemaker_session=sagemaker_session
    )

    # Trỏ input train và validation từ S3
    inputs = {
        'train': sagemaker.inputs.TrainingInput(train_data_uri, content_type='csv'),
        'validation': sagemaker.inputs.TrainingInput(val_data_uri, content_type='csv')
    }

    print("[INFO] Đẩy lệnh training lên AWS Cloud...")
    # Gọi estimator.fit() để khởi động job
    xgb_estimator.fit(inputs)

    # In tên job và đường dẫn model artifact sau khi hoàn thành
    print(f"\n[DONE] Training Job Name: {xgb_estimator.latest_training_job.job_name}")
    print(f"[DONE] Model Artifact S3 Path: {xgb_estimator.model_data}")

if __name__ == "__main__":
    run_training_job()