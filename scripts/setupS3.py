import boto3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

BUCKET = "amznce23"
REGION = "ap-southeast-1"
PROJECT = "T1_AD"

s3 = boto3.client("s3", region_name=REGION)

def upload_file(local_path, s3_key):
    s3.upload_file(local_path, BUCKET, s3_key)
    print(f" ⬆️ {local_path} → s3://{BUCKET}/{s3_key}")

print("📂 Upload dữ liệu thô...")
upload_file("data/raw/T1.csv", f"{PROJECT}/data/raw/T1.csv")

print("\n📂 Upload source code (src/)...")
for fname in os.listdir("src"):
    if fname.endswith(".py"):
        upload_file(f"src/{fname}", f"{PROJECT}/scripts/src/{fname}")

print("\n📂 Upload entry-point script...")
upload_file("src/preprocessing.py", f"{PROJECT}/scripts/preprocessing.py")

print(f"\n🎉 Upload hoàn tất!")
print(f" Raw data : s3://{BUCKET}/{PROJECT}/data/raw/T1.csv")
print(f" Scripts : s3://{BUCKET}/{PROJECT}/scripts/")