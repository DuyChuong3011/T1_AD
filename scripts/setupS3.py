"""
aws/setup_s3.py
================
Script tạo S3 bucket (nếu chưa có) và upload toàn bộ dữ liệu (raw, processed,
features) lên Amazon S3 bằng Python (boto3) — không cần vào AWS Console.

Bucket   : amznce23
Region   : ap-southeast-1

Cấu trúc thư mục local mong đợi:
    data/
    ├── raw/          (file CSV gốc, ví dụ turbine_5yr_labeled_data.csv)
    ├── processed/    (output của preprocessing.py, ví dụ scada_clean.csv)
    └── features/     (output của feature_engineering.py, ví dụ train.csv, test.csv)

Cấu trúc trên S3 sau khi upload:
    s3://amznce23/raw/...
    s3://amznce23/processed/...
    s3://amznce23/features/...

Yêu cầu trước khi chạy:
    - Đã cấu hình AWS credentials (chạy `aws configure` hoặc set biến môi trường
      AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_DEFAULT_REGION)
    - Đã cài boto3: pip install boto3

Cách dùng:
    python aws/setup_s3.py
    python aws/setup_s3.py --bucket amznce23 --region ap-southeast-1 --data-dir data
"""

import os
import argparse
import boto3
from botocore.exceptions import ClientError


def create_bucket(bucket_name: str, region: str) -> None:
    """Tạo S3 bucket nếu chưa tồn tại, bỏ qua nếu đã có.

    Tham số:
        bucket_name: tên bucket (KHÔNG dùng định dạng ARN, chỉ dùng tên thuần,
                     ví dụ 'amznce23' — không phải 'arn:aws:s3:::amznce23')
        region: region AWS (ví dụ 'ap-southeast-1')
    """
    s3_client = boto3.client("s3", region_name=region)

    try:
        # Các region khác us-east-1 cần khai báo LocationConstraint
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        print(f"[OK] Đã tạo bucket mới: {bucket_name}")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            # Bucket đã tồn tại (đúng trường hợp của bạn: amznce23 đã có sẵn) -> bỏ qua
            print(f"[SKIP] Bucket '{bucket_name}' đã tồn tại, dùng lại bucket này.")
        else:
            print(f"[ERROR] Không thể tạo bucket: {e}")
            raise


def upload_folder(local_folder: str, bucket: str, s3_prefix: str, region: str) -> int:
    """Duyệt toàn bộ file trong thư mục local (kể cả thư mục con) và upload lên S3.

    Tham số:
        local_folder: đường dẫn thư mục local cần upload (ví dụ 'data/raw')
        bucket: tên bucket đích
        s3_prefix: prefix (thư mục ảo) trên S3, ví dụ 'raw'
        region: region AWS

    Trả về:
        Số file đã upload thành công.
    """
    s3_client = boto3.client("s3", region_name=region)

    if not os.path.isdir(local_folder):
        print(f"[WARN] Thư mục không tồn tại, bỏ qua: {local_folder}")
        return 0

    uploaded_count = 0

    for root, _dirs, files in os.walk(local_folder):
        for filename in files:
            local_path = os.path.join(root, filename)

            # Giữ nguyên cấu trúc thư mục con khi đưa lên S3
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = f"{s3_prefix}/{relative_path}".replace("\\", "/")

            try:
                s3_client.upload_file(local_path, bucket, s3_key)
                size_kb = os.path.getsize(local_path) / 1024
                print(f"  [UPLOAD] {local_path} -> s3://{bucket}/{s3_key} ({size_kb:.1f} KB)")
                uploaded_count += 1
            except ClientError as e:
                print(f"  [ERROR] Lỗi upload {local_path}: {e}")

    return uploaded_count


def list_bucket(bucket: str, prefix: str, region: str) -> None:
    """In danh sách file hiện có trên S3 theo prefix, để kiểm tra lại sau khi upload.

    Tham số:
        bucket: tên bucket
        prefix: prefix cần lọc (ví dụ 'raw', 'processed', 'features')
        region: region AWS
    """
    s3_client = boto3.client("s3", region_name=region)

    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = response.get("Contents", [])

    if not contents:
        print(f"  (không có file nào với prefix '{prefix}/')")
        return

    for obj in contents:
        size_kb = obj["Size"] / 1024
        print(f"  - {obj['Key']} ({size_kb:.1f} KB, modified {obj['LastModified']})")


def main():
    parser = argparse.ArgumentParser(
        description="Upload dữ liệu turbine (raw/processed/features) lên S3."
    )
    parser.add_argument(
        "--bucket",
        default="amznce23",
        help="Tên S3 bucket (mặc định: amznce23)",
    )
    parser.add_argument(
        "--region",
        default="ap-southeast-1",
        help="AWS region (mặc định: ap-southeast-1)",
    )
    parser.add_argument(
        "--data-dir",
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
        help="Thư mục data gốc chứa raw/, processed/, features/ (mặc định: PRE_at/data, thư mục cha của scripts/)",
    )
    args = parser.parse_args()

    bucket = args.bucket
    region = args.region
    data_dir = args.data_dir

    print("=" * 60)
    print(f"Bucket : {bucket}")
    print(f"Region : {region}")
    print(f"Data dir: {data_dir}")
    print("=" * 60)

    # Bước 1: Tạo bucket (bỏ qua nếu đã tồn tại - bucket amznce23 đã có sẵn)
    print("\n[1/3] Tạo bucket (nếu chưa có)...")
    create_bucket(bucket, region)

    # Bước 2: Upload từng thư mục con theo đúng prefix tương ứng
    folders_to_upload = {
        "raw": os.path.join(data_dir, "raw"),
        "processed": os.path.join(data_dir, "processed"),
        "features": os.path.join(data_dir, "features"),
    }

    print("\n[2/3] Upload dữ liệu lên S3...")
    total_uploaded = 0
    for s3_prefix, local_folder in folders_to_upload.items():
        print(f"\n-> Đang upload '{local_folder}' lên 's3://{bucket}/{s3_prefix}/'")
        count = upload_folder(local_folder, bucket, s3_prefix, region)
        print(f"   Đã upload {count} file.")
        total_uploaded += count

    print(f"\nTổng số file đã upload: {total_uploaded}")

    # Bước 3: Kiểm tra lại bằng cách list bucket
    print("\n[3/3] Kiểm tra lại nội dung trên S3...")
    for s3_prefix in folders_to_upload:
        print(f"\ns3://{bucket}/{s3_prefix}/")
        list_bucket(bucket, s3_prefix, region)

    print("\nHoàn tất.")


if __name__ == "__main__":
    main()