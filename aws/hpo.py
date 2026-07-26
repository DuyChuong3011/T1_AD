import boto3
import sagemaker

from sagemaker.session import Session
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.tuner import HyperparameterTuner
from sagemaker.parameter import IntegerParameter, ContinuousParameter

def run_hpo():
    print("[INFO] Bắt đầu thiết lập Hyperparameter Tuning Job...")

    boto_session = boto3.Session()
    sagemaker_session = Session(boto_session=boto_session)

    role = "arn:aws:iam::795644302727:role/SageMakerExecutionRole-MLOps" 
    bucket = sagemaker_session.default_bucket()

    xgb_estimator = SKLearn(
        entry_point="src/train.py",
        framework_version="1.2-1",
        instance_type="ml.m5.xlarge", 
        instance_count=1,
        role=role,
        sagemaker_session=sagemaker_session,
    )

    hyperparameter_ranges = {
        "max_depth": IntegerParameter(3, 10),
        "n_estimators": IntegerParameter(50, 200),
        "learning_rate": ContinuousParameter(0.01, 0.3),
        "scale_pos_weight": ContinuousParameter(1.0, 10.0)
    }

    metric_definitions = [
        {"Name": "Validation-F1", "Regex": "Validation-F1: ([0-9\\.]+)"}
    ]

    tuner = HyperparameterTuner(
        estimator=xgb_estimator,
        objective_metric_name="Validation-F1",
        hyperparameter_ranges=hyperparameter_ranges,
        metric_definitions=metric_definitions,
        objective_type="Maximize",
        max_jobs=10,
        max_parallel_jobs=1,
    )

    print("[INFO] Đang đẩy kịch bản HPO lên Cloud SageMaker...")
    
    tuner.fit({
        "train": f"s3://{bucket}/data/features/train.csv",
        "test": f"s3://{bucket}/data/features/test.csv"
    })
    
    print(f"\n✅ Job HPO đã được đẩy lên thành công! Tên Job: {tuner.latest_tuning_job.name}")

if __name__ == "__main__":
    run_hpo()