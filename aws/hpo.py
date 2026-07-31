import sys
sys.stdout.reconfigure(encoding='utf-8')
import sagemaker
from sagemaker.xgboost.estimator import XGBoost
from sagemaker.tuner import IntegerParameter, ContinuousParameter, HyperparameterTuner
import boto3

def run_hpo_job():
    sagemaker_session = sagemaker.Session()
    role = "arn:aws:iam::795644302727:role/SageMakerExecutionRole-MLOps"
    bucket = "amznce23"
    
    # Định nghĩa đường dẫn dữ liệu Tuabin gió trên S3 
    output_path = f's3://{bucket}/hpo_models/'

    # Estimator nền tảng
    xgb_estimator = XGBoost(
        entry_point='train.py',
        source_dir='src',
        framework_version='1.7-1',
        role=role,
        instance_count=1,
        instance_type='ml.m5.large',
        output_path=output_path,
        sagemaker_session=sagemaker_session,
        hyperparameters={
            'scale_pos_weight': "10.0" # Giá trị tĩnh, không thể tune do giới hạn của AWS container
        }
    )

    # 1. Định nghĩa hyperparameter_ranges
    hyperparameter_ranges = {
        'max_depth': IntegerParameter(3, 10),
        'num_round': IntegerParameter(50, 200), 
        'eta': ContinuousParameter(0.01, 0.3),
        'subsample': ContinuousParameter(0.5, 1.0),
        'colsample_bytree': ContinuousParameter(0.5, 1.0),
        'alpha': ContinuousParameter(0.0, 10.0), # L1
        'lambda': ContinuousParameter(0.0, 10.0), # L2
        'gamma': ContinuousParameter(0.0, 5.0)
    }

    # XGBoost trên SageMaker (Script Mode) sẽ in kết quả ra log.
    # Cần Regex để bắt objective metric là F1 từ Terminal stdout
    metric_definitions = [{'Name': 'validation:f1', 'Regex': 'Validation-F1: ([0-9\\.]+)'}]

    # 2. Khởi tạo Hyperparameter Tuner
    tuner = HyperparameterTuner(
        estimator=xgb_estimator,
        objective_metric_name='validation:f1', # objective metric là validation:f1 (chuẩn của AWS)
        objective_type='Maximize',
        hyperparameter_ranges=hyperparameter_ranges,
        metric_definitions=metric_definitions,
        max_jobs=30, # max 30 jobs
        max_parallel_jobs=3 # chạy 3 job song song
    )

    inputs = {
        'train': f's3://{bucket}/features/T1_train_hybrid.csv',
        'validation': f's3://{bucket}/features/T1_test_hybrid.csv'
    }

    print("[INFO] Đang khởi động tiến trình Hyperparameter Tuning (HPO)...")
    # 3. Gọi tuner.fit() để khởi động
    tuner.fit(inputs)
    tuner.wait()

    # 4. Lấy tên job tốt nhất, in hyperparameters của job đó
    best_job_name = tuner.best_training_job()
    print(f"\n[WINNER] Tên Job tốt nhất: {best_job_name}")
    
    best_job_info = boto3.client('sagemaker').describe_training_job(TrainingJobName=best_job_name)
    print(f"[WINNER] Bộ siêu tham số tốt nhất:\n{best_job_info['HyperParameters']}")

if __name__ == "__main__":
    run_hpo_job()