"""
Deploy SageMaker Endpoint from Model Registry
Hỗ trợ auto-scaling, multi-AZ, và monitoring
"""

import boto3
import sagemaker
from sagemaker.model import ModelPackage
from datetime import datetime
import time

# Configuration
BUCKET = "amznce23"
PROJECT = "T1_AD"
REGION = "ap-southeast-1"
ROLE_ARN = "arn:aws:iam::795644302727:role/SageMakerExecutionRole-MLOps"
ENDPOINT_NAME = "scada-fault-prediction-endpoint"
MODEL_GROUP_NAME = "SCADA-Fault-Prediction"

# Initialize clients
boto_session = boto3.Session(region_name=REGION)
sagemaker_session = sagemaker.Session(boto_session=boto_session)
sm_client = boto_session.client("sagemaker")
autoscaling_client = boto_session.client("application-autoscaling")


def get_latest_approved_model():
    """
    Lấy model package mới nhất đã được approve từ Model Registry

    Returns:
        str: Model Package ARN
    """
    print("🔍 [Step 1] Đang tìm model mới nhất...")

    response = sm_client.list_model_packages(
        ModelPackageGroupName=MODEL_GROUP_NAME,
        ModelApprovalStatus="Approved",
        SortBy="CreationTime",
        SortOrder="Descending",
        MaxResults=1
    )

    if not response["ModelPackageSummaryList"]:
        raise RuntimeError("❌ Không có model approved nào trong Model Registry")

    model_package = response["ModelPackageSummaryList"][0]
    model_arn = model_package["ModelPackageArn"]
    model_version = model_package["ModelPackageName"]

    print(f"✅ Model version: {model_version}")
    print(f"✅ Model ARN: {model_arn}")

    return model_arn, model_version


def create_model(model_arn, model_name):
    """
    Tạo SageMaker Model từ Model Package

    Args:
        model_arn (str): Model Package ARN
        model_name (str): Tên của SageMaker Model

    Returns:
        str: Model ARN
    """
    print(f"\n📦 [Step 2] Đang tạo Model từ Model Package...")

    try:
        # Check if model already exists
        existing_model = sm_client.describe_model(ModelName=model_name)
        print(f"⚠️  Model {model_name} đã tồn tại, sử dụng model cũ")
        return existing_model["ModelArn"]
    except sm_client.exceptions.ValidationException:
        # Model doesn't exist, create new one
        pass

    response = sm_client.create_model(
        ModelName=model_name,
        PrimaryContainer={
            "ModelPackageName": model_arn,
        },
        ExecutionRoleArn=ROLE_ARN,
        Tags=[
            {"Key": "Project", "Value": PROJECT},
            {"Key": "Environment", "Value": "Production"},
            {"Key": "ManagedBy", "Value": "Terraform"}
        ]
    )

    model_arn = response["ModelArn"]
    print(f"✅ Model created: {model_arn}")

    return model_arn


def create_endpoint_config(model_arn, config_name, instance_type="ml.m5.xlarge", instance_count=1):
    """
    Tạo Endpoint Configuration

    Args:
        model_arn (str): Model ARN
        config_name (str): Tên của endpoint config
        instance_type (str): Instance type (ml.m5.large, ml.m5.xlarge, etc.)
        instance_count (int): Số instances (tối thiểu 1 cho single-AZ, 2+ cho multi-AZ)

    Returns:
        str: Endpoint Config name
    """
    print(f"\n⚙️  [Step 3] Đang tạo Endpoint Configuration...")

    try:
        # Check if config already exists
        sm_client.describe_endpoint_config(EndpointConfigName=config_name)
        print(f"⚠️  Endpoint Config {config_name} đã tồn tại, sử dụng cấu hình cũ")
        return config_name
    except sm_client.exceptions.ValidationException:
        pass

    response = sm_client.create_endpoint_config(
        EndpointConfigName=config_name,
        ProductionVariants=[
            {
                "VariantName": "Primary",
                "ModelName": model_arn.split("/")[-1],  # Extract model name from ARN
                "InitialInstanceCount": instance_count,
                "InstanceType": instance_type,
                "VariantWeight": 1.0,
                # Enable monitoring
                "DataCaptureConfig": {
                    "EnableCapture": True,
                    "InitialSamplingPercentage": 10,
                    "DestinationS3Uri": f"s3://{BUCKET}/{PROJECT}/endpoint-data-capture/",
                    "CaptureOptions": [
                        {"CaptureMode": "InputAndOutput"},
                    ]
                }
            }
        ],
        DataCaptureConfig={
            "EnableCapture": True,
            "InitialSamplingPercentage": 10,
            "DestinationS3Uri": f"s3://{BUCKET}/{PROJECT}/endpoint-data-capture/",
            "CaptureOptions": [
                {"CaptureMode": "InputAndOutput"},
            ]
        },
        Tags=[
            {"Key": "Project", "Value": PROJECT},
            {"Key": "Environment", "Value": "Production"}
        ]
    )

    config_name = response["EndpointConfigArn"].split("/")[-1]
    print(f"✅ Endpoint Config created: {config_name}")

    return config_name


def create_or_update_endpoint(endpoint_name, endpoint_config_name):
    """
    Tạo hoặc update SageMaker Endpoint

    Args:
        endpoint_name (str): Tên của endpoint
        endpoint_config_name (str): Tên của endpoint config

    Returns:
        str: Endpoint ARN
    """
    print(f"\n🚀 [Step 4] Đang deploy Endpoint: {endpoint_name}...")

    try:
        # Check if endpoint already exists
        endpoint_info = sm_client.describe_endpoint(EndpointName=endpoint_name)
        print(f"⚠️  Endpoint {endpoint_name} đã tồn tại")
        print(f"   Status: {endpoint_info['EndpointStatus']}")

        if endpoint_info["EndpointStatus"] == "InService":
            print(f"   Đang update endpoint configuration...")
            sm_client.update_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            print(f"✅ Endpoint updated, đang chờ hoàn tất (này có thể mất 5-10 phút)...")
            wait_for_endpoint(endpoint_name)
        else:
            print(f"   Endpoint hiện không available, vui lòng kiểm tra AWS Console")

        return endpoint_info["EndpointArn"]

    except sm_client.exceptions.ValidationException:
        # Endpoint doesn't exist, create new one
        print(f"   Tạo endpoint mới...")
        response = sm_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name,
            Tags=[
                {"Key": "Project", "Value": PROJECT},
                {"Key": "Environment", "Value": "Production"},
                {"Key": "CreatedAt", "Value": datetime.utcnow().isoformat()}
            ]
        )

        endpoint_arn = response["EndpointArn"]
        print(f"✅ Endpoint created: {endpoint_arn}")
        print(f"   Đang chờ endpoint sẵn sàng (này có thể mất 5-10 phút)...")

        wait_for_endpoint(endpoint_name)
        return endpoint_arn


def wait_for_endpoint(endpoint_name, max_wait_seconds=1200):
    """
    Đợi endpoint trở thành 'InService'

    Args:
        endpoint_name (str): Tên endpoint
        max_wait_seconds (int): Thời gian chờ tối đa (mặc định 20 phút)
    """
    print(f"⏳ Đang chờ endpoint {endpoint_name} trở thành InService...")

    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        endpoint_info = sm_client.describe_endpoint(EndpointName=endpoint_name)
        status = endpoint_info["EndpointStatus"]

        if status == "InService":
            print(f"✅ Endpoint {endpoint_name} is now InService!")
            return True
        elif status == "Failed":
            raise RuntimeError(f"❌ Endpoint {endpoint_name} failed to deploy")

        print(f"   Status: {status} (elapsed: {int(time.time() - start_time)}s)")
        time.sleep(30)

    raise TimeoutError(f"Endpoint {endpoint_name} did not become InService within {max_wait_seconds}s")


def setup_autoscaling(endpoint_name, min_instances=1, max_instances=4, target_utilization=70.0):
    """
    Setup Auto-Scaling cho SageMaker Endpoint

    Args:
        endpoint_name (str): Tên endpoint
        min_instances (int): Số instances tối thiểu
        max_instances (int): Số instances tối đa
        target_utilization (float): Target CPU utilization %
    """
    print(f"\n📊 [Step 5] Đang setup Auto-Scaling...")

    resource_id = f"endpoint/{endpoint_name}/variant/Primary"

    try:
        # Register scalable target
        autoscaling_client.register_scalable_target(
            ServiceNamespace="sagemaker",
            ResourceId=resource_id,
            ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            MinCapacity=min_instances,
            MaxCapacity=max_instances
        )

        print(f"✅ Scalable target registered")

        # Create scaling policy
        autoscaling_client.put_scaling_policy(
            PolicyName=f"{endpoint_name}-autoscaling",
            ServiceNamespace="sagemaker",
            ResourceId=resource_id,
            ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            PolicyType="TargetTrackingScaling",
            TargetTrackingScalingPolicyConfiguration={
                "TargetValue": target_utilization,
                "PredefinedMetricSpecification": {
                    "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
                },
                "ScaleOutCooldown": 60,
                "ScaleInCooldown": 300
            }
        )

        print(f"✅ Auto-Scaling policy created")
        print(f"   Min instances: {min_instances}")
        print(f"   Max instances: {max_instances}")
        print(f"   Target utilization: {target_utilization}%")

    except Exception as e:
        print(f"⚠️  Could not setup auto-scaling: {e}")


def print_endpoint_info(endpoint_name):
    """
    In ra thông tin endpoint

    Args:
        endpoint_name (str): Tên endpoint
    """
    endpoint_info = sm_client.describe_endpoint(EndpointName=endpoint_name)

    print("\n" + "="*70)
    print("🎉 ENDPOINT DEPLOYMENT COMPLETE")
    print("="*70)
    print(f"Endpoint Name      : {endpoint_info['EndpointName']}")
    print(f"Endpoint Status    : {endpoint_info['EndpointStatus']}")
    print(f"Endpoint ARN       : {endpoint_info['EndpointArn']}")
    print(f"Created Time       : {endpoint_info['CreationTime']}")
    print(f"Last Modified Time : {endpoint_info['LastModifiedTime']}")
    print(f"Instance Count     : {endpoint_info['ProductionVariants'][0]['CurrentInstanceCount']}")
    print(f"Instance Type      : {endpoint_info['ProductionVariants'][0]['InstanceType']}")
    print("="*70)


def main(model_package_arn=None, instance_type="ml.m5.xlarge", instance_count=1, enable_autoscaling=True):
    """
    Main deployment pipeline

    Args:
        model_package_arn (str): Model Package ARN. Nếu None, lấy mới nhất đã approve
        instance_type (str): Instance type
        instance_count (int): Số instances
        enable_autoscaling (bool): Enable auto-scaling
    """
    print("🚀 Starting SageMaker Endpoint Deployment...\n")

    try:
        # Step 1: Get latest approved model
        if model_package_arn is None:
            model_arn, model_version = get_latest_approved_model()
        else:
            model_arn = model_package_arn
            model_version = model_arn.split("/")[-1]

        # Step 2: Create Model
        model_name = f"scada-fault-model-{datetime.utcnow().strftime('%Y%m%d')}"
        create_model(model_arn, model_name)

        # Step 3: Create Endpoint Config
        config_name = f"scada-fault-config-{datetime.utcnow().strftime('%Y%m%d')}"
        create_endpoint_config(model_arn, config_name, instance_type, instance_count)

        # Step 4: Deploy Endpoint
        create_or_update_endpoint(ENDPOINT_NAME, config_name)

        # Step 5: Setup Auto-Scaling (nếu instance_count > 1)
        if enable_autoscaling and instance_count >= 1:
            setup_autoscaling(ENDPOINT_NAME, min_instances=instance_count, max_instances=4)

        # Print endpoint info
        print_endpoint_info(ENDPOINT_NAME)

        print("\n✅ Deployment hoàn tất! Endpoint sẵn sàng phục vụ prediction requests")

    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-package-arn",
        default=None,
        help="Model Package ARN. Nếu không, lấy latest approved model"
    )
    parser.add_argument(
        "--instance-type",
        default="ml.m5.xlarge",
        help="Instance type (ml.m5.large, ml.m5.xlarge, etc.)"
    )
    parser.add_argument(
        "--instance-count",
        type=int,
        default=1,
        help="Số instances"
    )
    parser.add_argument(
        "--no-autoscaling",
        action="store_true",
        help="Disable auto-scaling"
    )

    args = parser.parse_args()

    main(
        model_package_arn=args.model_package_arn,
        instance_type=args.instance_type,
        instance_count=args.instance_count,
        enable_autoscaling=not args.no_autoscaling
    )
