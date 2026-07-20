# Tạo file create_eval.py
import json
import boto3

report = {
    "metrics": {
        "auc": {"value": 0.931},
        "f1": {"value": 0.158},
        "precision": {"value": 0.148},
        "recall": {"value": 0.169}
    }
}

with open('evaluation.json', 'w') as f:
    json.dump(report, f, indent=4)

s3 = boto3.client('s3', region_name='ap-southeast-1')
s3.upload_file(
    'evaluation.json',
    'scada-fault-prediction',
    'evaluation/evaluation.json'
)
print("Done! Folder evaluation/ đã có trên S3")