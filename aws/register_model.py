import sys
sys.stdout.reconfigure(encoding='utf-8')
import sagemaker
import boto3

def register_best_model(best_training_job_name):
    sagemaker_session = sagemaker.Session()
    client = boto3.client('sagemaker')
    
    # 1. Lấy thông tin model artifact từ best HPO job
    job_info = client.describe_training_job(TrainingJobName=best_training_job_name)
    model_data_url = job_info['ModelArtifacts']['S3ModelArtifacts'] # Đường dẫn lấy từ best HPO job
    
    # 2. Đăng ký vào Model Registry
    model_package_group_name = "WindTurbineFaultDetectionGroup" # group name
    
    # Đảm bảo Group đã được tạo trước
    try:
        client.create_model_package_group(
            ModelPackageGroupName=model_package_group_name,
            ModelPackageGroupDescription="Nhóm các Model dự đoán lỗi hệ thống Tuabin gió"
        )
        print(f"[INFO] Đã tạo Model Group mới: {model_package_group_name}")
    except client.exceptions.ClientError as e:
        print(f"[INFO] Model Group {model_package_group_name} đã tồn tại.")

    print(f"[INFO] Đang đăng ký artifact {model_data_url} vào Registry...")
    # Tạo Package với Approval status 'Approved'
    response = client.create_model_package(
        ModelPackageGroupName=model_package_group_name,
        ModelPackageDescription="Model XGBoost tối ưu qua HPO với dữ liệu T1_train.csv", # description
        ModelApprovalStatus="Approved", # approval status Approved
        InferenceSpecification={
            "Containers": [{
                "Image": sagemaker.image_uris.retrieve("xgboost", sagemaker_session.boto_region_name, "1.7-1"),
                "ModelDataUrl": model_data_url
            }],
            "SupportedContentTypes": ["text/csv"],
            "SupportedResponseMIMETypes": ["text/csv"]
        }
    )

    # 3. In model package ARN ra terminal để người C copy
    model_package_arn = response['ModelPackageArn']
    print(f"\n[SUCCESS] Model đã được đăng ký thành công!")
    print(f"[ARN TO COPY] Model Package ARN: {model_package_arn}")

if __name__ == "__main__":
    # Thay thế chuỗi này bằng tên job in ra từ script training_job.py
    best_job_from_hpo = "sagemaker-xgboost-2026-07-29-06-53-53-231" 
    register_best_model(best_job_from_hpo)