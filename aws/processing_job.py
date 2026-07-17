"""
processing_job.py
=================
Chạy một SageMaker Processing job dùng SKLearnProcessor để thực thi bước
feature engineering (src/feature_engineering.py) trên dữ liệu đã tiền xử lý.

Luồng dữ liệu:
    s3://<bucket>/processed/  --(ProcessingInput)-->  /opt/ml/processing/input
    /opt/ml/processing/output --(ProcessingOutput)-->  s3://<bucket>/features/

Yêu cầu:
    - Đã cài: pip install sagemaker boto3
    - Đã cấu hình AWS credentials (aws configure hoặc biến môi trường)
    - Có IAM role (ARN) cho SageMaker với quyền truy cập S3 tương ứng

Cách dùng:
    python src/processing_job.py \
        --bucket amznce23 \
        --region ap-southeast-1 \
        --role arn:aws:iam::<account-id>:role/<SageMakerExecutionRole>
"""
import argparse
import os

import boto3
import sagemaker
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput


def run_processing_job(
    bucket: str,
    region: str,
    role: str,
    instance_type: str = "ml.m5.large",
    instance_count: int = 1,
    framework_version: str = "1.2-1",
):
    """Khởi tạo và chạy SageMaker Processing job cho feature engineering."""

    input_s3 = f"s3://{bucket}/processed/"
    output_s3 = f"s3://{bucket}/features/"

    # 1) Khởi tạo SKLearnProcessor (instance ml.m5.large, role, region)
    boto_session = boto3.Session(region_name=region)
    sm_session = sagemaker.Session(boto_session=boto_session)
    processor = SKLearnProcessor(
        framework_version=framework_version,
        role=role,
        instance_type=instance_type,
        instance_count=instance_count,
        base_job_name="feature-engineering",
        sagemaker_session=sm_session,
    )

    # 2) ProcessingInput trỏ vào s3://bucket/processed/
    proc_input = ProcessingInput(
        source=input_s3,
        destination="/opt/ml/processing/input",
        input_name="processed-data",
    )

    # 3) ProcessingOutput trỏ ra s3://bucket/features/
    proc_output = ProcessingOutput(
        source="/opt/ml/processing/output",
        destination=output_s3,
        output_name="features-data",
    )

    # 4) Chạy job, truyền vào src/feature_engineering.py làm entry-point
    # Tìm đường dẫn src/ từ vị trí file hiện tại (aws/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    code_path = os.path.join(project_root, "src", "feature_engineering.py")
    print("=" * 60)
    print(f"Region        : {region}")
    print(f"Instance type : {instance_type} x{instance_count}")
    print(f"Input         : {input_s3}")
    print(f"Output        : {output_s3}")
    print(f"Code          : {code_path}")
    print("=" * 60)
    print("Đang gửi Processing job lên SageMaker (chờ hoàn thành)...")

    processor.run(
        code=code_path,
        inputs=[proc_input],
        outputs=[proc_output],
        wait=True,
        logs=True,
    )

    # 5) In trạng thái và đường dẫn output sau khi job hoàn thành
    job_desc = processor.latest_job.describe()
    status = job_desc.get("ProcessingJobStatus", "Unknown")

    print("\n" + "=" * 60)
    print(f"Trạng thái job   : {status}")
    print(f"Tên job          : {job_desc.get('ProcessingJobName')}")
    print(f"Đường dẫn output : {output_s3}")
    if status == "Completed":
        print("Job hoàn thành — kết quả feature engineering đã ghi vào features/.")
    else:
        print(f"Job kết thúc với trạng thái '{status}'. Xem CloudWatch logs để biết chi tiết.")
    print("=" * 60)

    return status, output_s3


def main():
    parser = argparse.ArgumentParser(
        description="Chạy SageMaker Processing job cho feature engineering (processed/ -> features/)."
    )
    parser.add_argument("--bucket", required=True, help="Tên S3 bucket")
    parser.add_argument("--region", default="ap-southeast-1", help="AWS region (mặc định: ap-southeast-1)")
    parser.add_argument("--role", required=True, help="ARN của IAM role cho SageMaker")
    parser.add_argument("--instance-type", default="ml.m5.large", help="Loại instance (mặc định: ml.m5.large)")
    parser.add_argument("--instance-count", type=int, default=1, help="Số instance (mặc định: 1)")
    parser.add_argument("--framework-version", default="1.2-1", help="Phiên bản scikit-learn container")
    args = parser.parse_args()

    run_processing_job(
        bucket=args.bucket,
        region=args.region,
        role=args.role,
        instance_type=args.instance_type,
        instance_count=args.instance_count,
        framework_version=args.framework_version,
    )


if __name__ == "__main__":
    main()
