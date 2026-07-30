"""
Register trained model to SageMaker Model Registry
Cho phép version control và approval workflow
"""

import boto3
import sagemaker
from sagemaker.model import Model
from datetime import datetime

# Configuration
BUCKET = "amznce23"
PROJECT = "T1_AD"
REGION = "ap-southeast-1"
ROLE_ARN = "arn:aws:iam::795644302727:role/SageMakerExecutionRole-MLOps"
MODEL_GROUP_NAME = "SCADA-Fault-Prediction"

# Initialize clients
boto_session = boto3.Session(region_name=REGION)
sagemaker_session = sagemaker.Session(boto_session=boto_session)
sm_client = boto_session.client("sagemaker")


def register_model_to_registry(training_job_name, model_version=None):
    """
    Đăng ký model từ training job vào SageMaker Model Registry

    Args:
        training_job_name (str): Tên của training job (vd: 't1-ad-xgboost-20240730-...')
        model_version (str): Phiên bản model (vd: 'v1.0'). Nếu None, auto-generate timestamp

    Returns:
        dict: Model package group details
    """

    print(f"🔍 [Step 1] Đang lấy thông tin training job: {training_job_name}")

    # Get training job details
    training_job = sm_client.describe_training_job(TrainingJobName=training_job_name)
    model_uri = training_job["ModelArtifacts"]["S3ModelArtifacts"]
    image_uri = training_job["AlgorithmSpecification"]["TrainingImage"]

    print(f"✅ Model URI: {model_uri}")
    print(f"✅ Image URI: {image_uri}")

    # ─── STEP 2: Create Model Package Group (nếu chưa tồn tại) ───
    print(f"\n📦 [Step 2] Kiểm tra Model Package Group: {MODEL_GROUP_NAME}")

    try:
        group_info = sm_client.describe_model_package_group(
            ModelPackageGroupName=MODEL_GROUP_NAME
        )
        print(f"✅ Model Package Group đã tồn tại")
    except sm_client.exceptions.EntityNotFound:
        print(f"⚠️  Model Package Group chưa tồn tại, đang tạo...")
        sm_client.create_model_package_group(
            ModelPackageGroupName=MODEL_GROUP_NAME,
            ModelPackageGroupDescription="SCADA Fault Prediction - XGBoost Models",
            Tags=[
                {"Key": "Project", "Value": PROJECT},
                {"Key": "Region", "Value": REGION}
            ]
        )
        print(f"✅ Model Package Group đã được tạo")

    # ─── STEP 3: Tạo Model Package (phiên bản model) ───
    if model_version is None:
        model_version = datetime.now().strftime("v%Y%m%d_%H%M%S")

    model_package_name = f"{MODEL_GROUP_NAME}-{model_version}"

    print(f"\n📝 [Step 3] Đang tạo Model Package: {model_package_name}")

    model_package_response = sm_client.create_model_package(
        ModelPackageGroupName=MODEL_GROUP_NAME,
        ModelPackageName=model_package_name,
        ModelPackageDescription=f"XGBoost model for SCADA fault prediction - {model_version}",
        InferenceSpecification={
            "Containers": [
                {
                    "Image": image_uri,
                    "ModelDataUrl": model_uri,
                    "Framework": "XGBOOST",
                    "FrameworkVersion": "1.2-1",
                }
            ],
            "SupportedContentTypes": ["text/csv", "application/json"],
            "SupportedResponseMIMETypes": ["application/json"],
        },
        ValidationSpecification={
            "ValidationRole": ROLE_ARN,
            "ValidationProfiles": [
                {
                    "ProfileName": "default",
                    "TransformJobDefinition": {
                        "MaxConcurrentTransforms": 1,
                        "MaxPayloadInMB": 100,
                        "BatchStrategy": "SingleRecord",
                        "Environment": {"XGBOOST_USE_NORMAL": "true"},
                        "TransformInput": {
                            "DataSource": {
                                "S3DataSource": {
                                    "S3DataType": "S3Prefix",
                                    "S3Uri": f"s3://{BUCKET}/{PROJECT}/data/test/"
                                }
                            },
                            "ContentType": "text/csv",
                        },
                        "TransformOutput": {
                            "S3OutputPath": f"s3://{BUCKET}/{PROJECT}/predictions/"
                        },
                        "TransformResources": {
                            "InstanceType": "ml.m5.large",
                            "InstanceCount": 1
                        }
                    }
                }
            ]
        },
        ModelMetrics={
            "ModelQuality": {
                "Statistics": {
                    "ContentType": "application/json",
                    "S3Uri": f"s3://{BUCKET}/{PROJECT}/model_metrics/quality.json"
                }
            }
        },
        Tags=[
            {"Key": "TrainingJob", "Value": training_job_name},
            {"Key": "ModelVersion", "Value": model_version},
            {"Key": "Project", "Value": PROJECT},
            {"Key": "Environment", "Value": "Production"}
        ]
    )

    model_package_arn = model_package_response["ModelPackageArn"]
    print(f"✅ Model Package ARN: {model_package_arn}")

    # ─── STEP 4: Output thông tin model ───
    print("\n" + "="*60)
    print("🎉 MODEL REGISTRY INFORMATION")
    print("="*60)
    print(f"Model Group Name    : {MODEL_GROUP_NAME}")
    print(f"Model Package Name  : {model_package_name}")
    print(f"Model Version       : {model_version}")
    print(f"Model Package ARN   : {model_package_arn}")
    print(f"Training Job        : {training_job_name}")
    print(f"Model Artifact URI  : {model_uri}")
    print("="*60)

    return {
        "model_package_name": model_package_name,
        "model_package_arn": model_package_arn,
        "model_version": model_version,
        "model_group_name": MODEL_GROUP_NAME
    }


def approve_model(model_package_name):
    """
    Approve model package để sử dụng cho inference
    (Thường dùng trong production workflow)
    """
    print(f"\n✅ [Step 4] Đang approve model: {model_package_name}")

    sm_client.update_model_package(
        ModelPackageName=model_package_name,
        ModelApprovalStatus="Approved"
    )

    print(f"✅ Model đã được approve!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--training-job-name",
        required=True,
        help="Tên của SageMaker training job (vd: t1-ad-xgboost-20240730-123456)"
    )
    parser.add_argument(
        "--model-version",
        default=None,
        help="Phiên bản model (vd: v1.0). Nếu không, dùng timestamp"
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Tự động approve model sau khi register"
    )

    args = parser.parse_args()

    # Register model
    result = register_model_to_registry(
        training_job_name=args.training_job_name,
        model_version=args.model_version
    )

    # Approve nếu flag được set
    if args.approve:
        approve_model(result["model_package_name"])

    print("\n✅ Hoàn tất! Model đã được register vào Model Registry")
