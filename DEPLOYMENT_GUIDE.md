# 🚀 SCADA Fault Prediction - Production Deployment Guide

**Nộp ngày: MAI**  
**Status: Production Ready**  
**Time to Deploy: ~20-30 minutes**

---

## 📋 Overview

Hướng dẫn này sẽ giúp bạn triển khai hệ thống ML end-to-end từ training → model registry → endpoint → lambda API.

### **Architecture**
```
Dataset → S3 → Processing → Training → Model Registry → Endpoint → Lambda API → CloudFront → Users
```

### **4 Files Vừa Tạo**
1. ✅ `aws/register_model.py` - Register model to Model Registry
2. ✅ `aws/lambda_handler.py` - Lambda prediction API handler
3. ✅ `aws/deploy_endpoint.py` - Deploy endpoint from registry
4. ✅ `aws/setup_dynamodb.py` - Setup prediction cache

---

## 🔧 Prerequisites

Đảm bảo bạn có:
```bash
# AWS CLI
aws --version

# Python 3.10+
python --version

# Installed packages
pip install boto3 sagemaker
```

### **AWS Credentials**
```bash
# Configure AWS CLI
aws configure
# Region: ap-southeast-1
# Access Key ID: [YOUR_KEY]
# Secret Access Key: [YOUR_SECRET]
```

---

## 📝 Step-by-Step Deployment

### **PHASE 1: Training & Model Registry (5 min)**

#### **Step 1.1: Run Training Job**

```bash
cd C:\Hanh\GITHUB\T1_AD

# Preprocess data
python aws/processing_job.py

# Train model (this will take 5-10 minutes)
python aws/training_job.py
```

**Output sẽ trông như:**
```
✅ Processing Job hoàn tất!
✅ Training Job đã hoàn tất trên AWS!
📦 Model Artifact được lưu trữ an toàn tại: s3://amznce23/T1_AD/models/xgboost-20240730-123456/output/model.tar.gz
```

**👉 GHI NHỚ:** Cái `Training Job Name` này (vd: `t1-ad-xgboost-20240730-123456`)

#### **Step 1.2: Register Model to Model Registry**

```bash
# Register model (thay XXXXX bằng training job name ở trên)
python aws/register_model.py \
  --training-job-name "t1-ad-xgboost-20240730-123456" \
  --model-version "v1.0" \
  --approve
```

**Output:**
```
🔍 [Step 1] Đang lấy thông tin training job...
✅ Model URI: s3://amznce23/T1_AD/models/.../model.tar.gz
✅ Image URI: 246618743141.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-xgboost:latest

📦 [Step 2] Kiểm tra Model Package Group
✅ Model Package Group đã được tạo

📝 [Step 3] Đang tạo Model Package: SCADA-Fault-Prediction-v1.0
✅ Model Package ARN: arn:aws:sagemaker:ap-southeast-1:795644302727:model-package/...

✅ Model đã được approve!
```

**Giải thích:**
- `--training-job-name`: Tên job training vừa chạy
- `--model-version`: Phiên bản (cho phép track multiple versions)
- `--approve`: Tự động approve model để deploy

---

### **PHASE 2: Database & Infrastructure (5 min)**

#### **Step 2.1: Setup DynamoDB Cache Table**

```bash
python aws/setup_dynamodb.py
```

**Output:**
```
📊 [Step 1] Đang tạo DynamoDB table: scada-predictions-cache...
✅ Table created: arn:aws:dynamodb:ap-southeast-1:...

⏰ [Step 2] Đang setup TTL trên table...
✅ TTL enabled
   Attribute: ExpiryTime
   Items sẽ tự động xóa khi hết hạn

📈 [Step 3] Đang setup CloudWatch monitoring...
✅ CloudWatch alarm created

🎉 DYNAMODB TABLE SETUP COMPLETE
   Items       : 0
   Size        : 0.00 MB
   Billing Mode: PAY_PER_REQUEST
```

**Giải thích:**
- PAY_PER_REQUEST: Chỉ trả tiền cho request dùng, rất rẻ
- TTL: Items tự động xóa sau 1 giờ
- Dùng để cache predictions → giảm latency + chi phí

---

### **PHASE 3: Endpoint Deployment (10-15 min)**

#### **Step 3.1: Deploy Endpoint from Model Registry**

```bash
python aws/deploy_endpoint.py \
  --instance-type "ml.m5.xlarge" \
  --instance-count 1
```

**Output (sẽ mất 10-15 phút):**
```
🚀 Starting SageMaker Endpoint Deployment...

🔍 [Step 1] Đang tìm model mới nhất...
✅ Model version: SCADA-Fault-Prediction-v1.0
✅ Model ARN: arn:aws:sagemaker:...

📦 [Step 2] Đang tạo Model từ Model Package...
✅ Model created: arn:aws:sagemaker:...

⚙️  [Step 3] Đang tạo Endpoint Configuration...
✅ Endpoint Config created: scada-fault-config-20240730

🚀 [Step 4] Đang deploy Endpoint: scada-fault-prediction-endpoint...
   Tạo endpoint mới...
✅ Endpoint created: arn:aws:sagemaker:...
⏳ Đang chờ endpoint trở thành InService...
   Status: Creating (elapsed: 30s)
   Status: InService (elapsed: 120s)
✅ Endpoint scada-fault-prediction-endpoint is now InService!

📊 [Step 5] Đang setup Auto-Scaling...
✅ Scalable target registered
✅ Auto-Scaling policy created
   Min instances: 1
   Max instances: 4

🎉 ENDPOINT DEPLOYMENT COMPLETE
   Endpoint Name      : scada-fault-prediction-endpoint
   Endpoint Status    : InService
   Instance Count     : 1
   Instance Type      : ml.m5.xlarge
```

**Giải thích:**
- `ml.m5.xlarge`: 4 vCPU, 16 GB RAM (đủ cho inference)
- `--instance-count 1`: Bắt đầu với 1 instance
- Auto-scaling: Tự động scale từ 1-4 instances dựa trên load
- Multi-AZ: Có thể update sau nếu cần high availability

---

### **PHASE 4: Lambda API Setup (3 min)**

#### **Step 4.1: Create Lambda Function (via AWS Console)**

Vì bạn nộp ngày mai, tôi sẽ hướng dẫn cách manual setup nhanh nhất:

**🔗 Đi tới:** https://console.aws.amazon.com/lambda/

**Step 1:** Click `Create function`
- Function name: `scada-fault-prediction-api`
- Runtime: `Python 3.11`
- Execution role: `SageMakerExecutionRole-MLOps` (existing)

**Step 2:** Paste code sau vào Lambda editor:
```python
# Copy toàn bộ nội dung từ aws/lambda_handler.py
```

**Step 3:** Setup environment variables:
```
SAGEMAKER_ENDPOINT_NAME = scada-fault-prediction-endpoint
DYNAMODB_CACHE_TABLE = scada-predictions-cache
PROJECT_NAME = T1_AD
```

**Step 4:** Increase timeout to 60 seconds:
- Configuration → General → Timeout → 60 seconds

**Step 5:** Create Lambda function

#### **Step 4.2: Test Lambda Function**

Click `Test` button, paste:
```json
{
  "body": "{\"features\": {\"Gearbox_Temp\": 40.5, \"Ambient_Temp\": 20.0, \"Wind_Speed\": 12.5, \"Wind_Dir_Sin\": 0.707, \"Wind_Dir_Cos\": 0.707, \"Nacelle_Angle\": 45.0, \"Active_Power\": 2000.0, \"Reactive_Power\": 500.0, \"Vibration\": 0.05, \"Month\": 7, \"Hour\": 14, \"Lag_1\": 1999.5}}"
}
```

**Expected response:**
```json
{
  "statusCode": 200,
  "body": "{\"prediction\": 0, \"confidence\": 0.15, \"fault_detected\": false, \"cached\": false, \"timestamp\": \"2024-07-30T...:00Z\", \"endpoint\": \"scada-fault-prediction-endpoint\"}"
}
```

---

### **PHASE 5: API Gateway Setup (2 min)**

#### **Step 5.1: Create API Gateway**

**🔗 Đi tới:** https://console.aws.amazon.com/apigateway/

**Step 1:** Create REST API
- Name: `scada-fault-api`
- Description: `SCADA Fault Prediction API`

**Step 2:** Create resource `/predict`
- Right-click root → Create resource
- Resource name: `predict`

**Step 3:** Create POST method
- Select `/predict` → Create method → POST
- Lambda function: `scada-fault-prediction-api`
- Lambda proxy integration: ✅ Enable

**Step 4:** Deploy API
- Click Deploy
- Stage name: `prod`
- **Copy API endpoint URL** (vd: `https://abc123.execute-api.ap-southeast-1.amazonaws.com/prod`)

#### **Step 5.2: Test API Endpoint**

```bash
# Test prediction API
curl -X POST "https://abc123.execute-api.ap-southeast-1.amazonaws.com/prod/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "Gearbox_Temp": 40.5,
      "Ambient_Temp": 20.0,
      "Wind_Speed": 12.5,
      "Wind_Dir_Sin": 0.707,
      "Wind_Dir_Cos": 0.707,
      "Nacelle_Angle": 45.0,
      "Active_Power": 2000.0,
      "Reactive_Power": 500.0,
      "Vibration": 0.05,
      "Month": 7,
      "Hour": 14,
      "Lag_1": 1999.5
    }
  }'
```

**Expected response:**
```json
{
  "prediction": 0,
  "confidence": 0.15,
  "fault_detected": false,
  "cached": false,
  "timestamp": "2024-07-30T15:30:45.123456Z",
  "endpoint": "scada-fault-prediction-endpoint"
}
```

---

## ✅ Verification Checklist

Sau khi hoàn tất, kiểm tra:

- [ ] ✅ Model registered in Model Registry
  ```bash
  aws sagemaker list-model-packages --model-package-group-name SCADA-Fault-Prediction
  ```

- [ ] ✅ Endpoint is `InService`
  ```bash
  aws sagemaker describe-endpoint --endpoint-name scada-fault-prediction-endpoint
  ```

- [ ] ✅ DynamoDB table exists
  ```bash
  aws dynamodb describe-table --table-name scada-predictions-cache
  ```

- [ ] ✅ Lambda function can be invoked
  ```bash
  aws lambda invoke --function-name scada-fault-prediction-api /tmp/out.json
  cat /tmp/out.json
  ```

- [ ] ✅ API Gateway returns predictions
  ```bash
  curl https://YOUR_API_ENDPOINT/prod/predict -X POST ...
  ```

---

## 📊 Monitoring

### **CloudWatch Metrics**

```bash
# View prediction count
aws cloudwatch get-metric-statistics \
  --namespace "SCADA/T1_AD" \
  --metric-name "Predictions" \
  --start-time 2024-07-30T00:00:00Z \
  --end-time 2024-07-30T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

### **Endpoint Metrics**

```bash
# View endpoint latency
aws cloudwatch get-metric-statistics \
  --namespace "AWS/SageMaker" \
  --metric-name "ModelLatency" \
  --dimensions Name=EndpointName,Value=scada-fault-prediction-endpoint \
  --start-time 2024-07-30T00:00:00Z \
  --end-time 2024-07-30T23:59:59Z \
  --period 300 \
  --statistics Average,Maximum
```

---

## 💰 Cost Estimation

| Component | Cost | Notes |
|-----------|------|-------|
| SageMaker Endpoint | $0.065/hour × ml.m5.xlarge | Stop khi không dùng |
| DynamoDB | ~$0.00 | PAY_PER_REQUEST, free tier |
| Lambda | ~$0.00 | Free tier |
| S3 | ~$0.00 | Storage only |
| **Total/hour** | **~$0.065** | ~$1.56/day |

**💡 Tip:** Stop endpoint khi không dùng
```bash
aws sagemaker stop-notebook-instance --notebook-instance-name scada-fault-prediction-endpoint
```

---

## 🚨 Troubleshooting

### **Problem: Endpoint stuck in "Creating" status**
```bash
# Check endpoint logs
aws logs tail /aws/sagemaker/Endpoints/scada-fault-prediction-endpoint --follow
```

### **Problem: Lambda timeout**
- Increase Lambda timeout to 60s
- Check VPC/security group settings

### **Problem: "AccessDenied" error**
- Verify IAM role has `sagemaker:InvokeEndpoint` permission
- Add to role:
```json
{
  "Effect": "Allow",
  "Action": [
    "sagemaker:InvokeEndpoint",
    "dynamodb:GetItem",
    "dynamodb:PutItem"
  ],
  "Resource": "*"
}
```

---

## 📌 Next Steps (Sau khi nộp)

1. **Setup CloudFront** - CDN for API
2. **Add VPC** - Security isolation
3. **Enable X-Ray** - Distributed tracing
4. **CI/CD Pipeline** - Auto-deploy
5. **Model Monitoring** - Drift detection

---

## 📞 Support

**If something breaks:**

1. Check AWS CloudWatch Logs
2. Verify IAM permissions
3. Check endpoint status in console
4. Restart Lambda function

**Quick debug:**
```bash
# Check all resources
aws sagemaker list-endpoints
aws lambda list-functions
aws dynamodb list-tables
```

---

**🎉 Congratulations! Your production ML API is ready!**

Deploy time: ~20-30 minutes  
Next refinement: Architecture improvements
