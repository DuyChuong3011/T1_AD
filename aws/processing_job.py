import boto3
import sagemaker
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ── Cấu hình ────────────────────────────────────────────────────
BUCKET = "amznce23"
PROJECT = "T1_AD"
ROLE = "arn:aws:iam::795644302727:role/SageMaker-DataEngineering-WindTurbine-Role" 
# LƯU Ý QUAN TRỌNG: SageMaker yêu cầu IAM Role (arn:aws:iam::...:role/...) thay vì IAM User.
# Nếu script báo lỗi "AccessDenied" hoặc "Invalid arn", bạn cần vào AWS IAM tạo một Role 
# (như hướng dẫn Bước 3) và dán ARN của Role đó vào đây nhé.

session = boto3.Session(region_name="ap-southeast-1")
sagemaker_session = sagemaker.Session(boto_session=session)

# ── Processor ───────────────────────────────────────────────────
processor = SKLearnProcessor(
    framework_version="1.2-1",
    role=ROLE,
    instance_count=1,
    instance_type="ml.m5.large",
    base_job_name="t1-ad-preprocessing",
    sagemaker_session=sagemaker_session
)

# ── Submit Job ───────────────────────────────────────────────────
print("🚀 Đang submit SageMaker Processing Job...")
processor.run(
    code=f"s3://{BUCKET}/{PROJECT}/scripts/preprocessing.py",
    inputs=[
        ProcessingInput(
            input_name="data",
            source=f"s3://{BUCKET}/{PROJECT}/data/raw/",
            destination="/opt/ml/processing/input/data"
        ),
        ProcessingInput(
            input_name="src_code",
            source=f"s3://{BUCKET}/{PROJECT}/scripts/src/",
            destination="/opt/ml/processing/input/code/src"
        ),
    ],
    outputs=[
        ProcessingOutput(
            output_name="processed",
            source="/opt/ml/processing/output/processed",
            destination=f"s3://{BUCKET}/{PROJECT}/data/processed/"
        ),
        ProcessingOutput(
            output_name="train",
            source="/opt/ml/processing/output/train",
            destination=f"s3://{BUCKET}/{PROJECT}/data/features/train/"
        ),
        ProcessingOutput(
            output_name="test",
            source="/opt/ml/processing/output/test",
            destination=f"s3://{BUCKET}/{PROJECT}/data/features/test/"
        ),
    ],
    arguments=["--train-ratio", "0.7"],
    wait=True,
    logs=True
)

print("\n✅ Processing Job hoàn tất!")
print(f" Processed : s3://{BUCKET}/{PROJECT}/data/processed/")
print(f" Train     : s3://{BUCKET}/{PROJECT}/data/features/train/")
print(f" Test      : s3://{BUCKET}/{PROJECT}/data/features/test/")
