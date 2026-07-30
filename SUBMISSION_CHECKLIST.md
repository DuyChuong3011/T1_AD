# ✅ SUBMISSION CHECKLIST - Nộp Ngày Mai

**Prepared:** 2024-07-30  
**Deadline:** TOMORROW  
**Status:** Ready to Deploy  

---

## 📋 Pre-Deployment (Do Today)

- [ ] **Read QUICK_START.md** (5 min)
  - Get overview of deployment
  - Understand each step

- [ ] **Install dependencies** (2 min)
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Configure AWS CLI** (2 min)
  ```bash
  aws configure
  # Region: ap-southeast-1
  # Access Key: [YOUR_KEY]
  # Secret Key: [YOUR_SECRET]
  ```

- [ ] **Verify AWS access** (1 min)
  ```bash
  aws s3 ls s3://amznce23/T1_AD/
  ```

---

## 🚀 Deployment Day (Tomorrow)

### **PHASE 1: Training & Registration (10 min)**

- [ ] **Run preprocessing**
  ```bash
  python aws/processing_job.py
  ```
  ✅ Output: `✅ Processing Job hoàn tất!`

- [ ] **Run training**
  ```bash
  python aws/training_job.py
  ```
  ✅ Output: `✅ Training Job đã hoàn tất`
  📝 **COPY training job name** (you'll need it)

- [ ] **Register model**
  ```bash
  python aws/register_model.py \
    --training-job-name "PASTE_JOB_NAME_HERE" \
    --model-version "v1.0" \
    --approve
  ```
  ✅ Output: `✅ Model đã được approve!`

### **PHASE 2: Setup Infrastructure (5 min)**

- [ ] **Create DynamoDB cache**
  ```bash
  python aws/setup_dynamodb.py
  ```
  ✅ Output: `✅ Setup hoàn tất! DynamoDB table sẵn sàng`

### **PHASE 3: Deploy Endpoint (15 min)**

- [ ] **Deploy endpoint**
  ```bash
  python aws/deploy_endpoint.py \
    --instance-type "ml.m5.xlarge" \
    --instance-count 1
  ```
  ✅ Output: `✅ Endpoint scada-fault-prediction-endpoint is now InService!`
  ⏳ **Wait up to 15 minutes for endpoint to become InService**

- [ ] **Verify endpoint status**
  ```bash
  aws sagemaker describe-endpoint \
    --endpoint-name scada-fault-prediction-endpoint \
    | grep EndpointStatus
  ```
  ✅ Expected: `"EndpointStatus": "InService"`

### **PHASE 4: Setup Lambda & API Gateway (5-10 min)**

#### **Step 1: Create Lambda Function**

- [ ] **Go to AWS Lambda Console**
  https://console.aws.amazon.com/lambda/

- [ ] **Create function:**
  - [ ] Function name: `scada-fault-prediction-api`
  - [ ] Runtime: `Python 3.11`
  - [ ] Execution role: `SageMakerExecutionRole-MLOps`

- [ ] **Copy Lambda code:**
  - [ ] Open file: `aws/lambda_handler.py`
  - [ ] Copy entire file content
  - [ ] Paste into Lambda editor
  - [ ] Deploy

- [ ] **Set environment variables:**
  - [ ] `SAGEMAKER_ENDPOINT_NAME` = `scada-fault-prediction-endpoint`
  - [ ] `DYNAMODB_CACHE_TABLE` = `scada-predictions-cache`
  - [ ] `PROJECT_NAME` = `T1_AD`

- [ ] **Configure timeout:**
  - [ ] Configuration tab
  - [ ] General settings
  - [ ] Timeout: **60 seconds**
  - [ ] Save

- [ ] **Test Lambda:**
  - [ ] Click `Test` button
  - [ ] Create new test event:
    ```json
    {
      "body": "{\"features\": {\"Gearbox_Temp\": 40.5, \"Ambient_Temp\": 20.0, \"Wind_Speed\": 12.5, \"Wind_Dir_Sin\": 0.707, \"Wind_Dir_Cos\": 0.707, \"Nacelle_Angle\": 45.0, \"Active_Power\": 2000.0, \"Reactive_Power\": 500.0, \"Vibration\": 0.05, \"Month\": 7, \"Hour\": 14, \"Lag_1\": 1999.5}}"
    }
    ```
  - [ ] Run test
  - [ ] ✅ Expected status: `200 OK`

#### **Step 2: Create API Gateway**

- [ ] **Go to API Gateway Console**
  https://console.aws.amazon.com/apigateway/

- [ ] **Create REST API:**
  - [ ] Name: `scada-fault-api`
  - [ ] Description: `SCADA Fault Prediction API`

- [ ] **Create resource `/predict`:**
  - [ ] Right-click root resource
  - [ ] Create resource
  - [ ] Resource name: `predict`

- [ ] **Create POST method:**
  - [ ] Select `/predict`
  - [ ] Create method → POST
  - [ ] Lambda function: `scada-fault-prediction-api`
  - [ ] Enable Lambda proxy integration: ✅ YES
  - [ ] Save

- [ ] **Deploy API:**
  - [ ] Click Deploy
  - [ ] Stage name: `prod`
  - [ ] Deploy
  - [ ] **COPY API endpoint URL** (you'll need it)
    ```
    https://abc123.execute-api.ap-southeast-1.amazonaws.com/prod
    ```

- [ ] **Test API endpoint:**
  - [ ] Use curl or Postman:
    ```bash
    curl -X POST "YOUR_API_URL/predict" \
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
  - [ ] ✅ Expected response:
    ```json
    {
      "prediction": 0,
      "confidence": 0.15,
      "fault_detected": false,
      "cached": false,
      "timestamp": "2024-07-30T...",
      "endpoint": "scada-fault-prediction-endpoint"
    }
    ```

---

## 📸 Verification & Screenshots (5 min)

### **Screenshot 1: Endpoint Status**

- [ ] Go to AWS SageMaker Console
- [ ] Endpoints → `scada-fault-prediction-endpoint`
- [ ] Verify Status: `InService` ✅
- [ ] **Screenshot:** Endpoint details page
- [ ] Save as: `screenshot_1_endpoint.png`

### **Screenshot 2: Lambda Test**

- [ ] Go to AWS Lambda Console
- [ ] Function: `scada-fault-prediction-api`
- [ ] Click Test
- [ ] Run test with sample data
- [ ] **Screenshot:** Test result showing `statusCode: 200`
- [ ] Save as: `screenshot_2_lambda_test.png`

### **Screenshot 3: API Response**

- [ ] Run curl command (or use Postman)
- [ ] Get successful prediction response
- [ ] **Screenshot:** Terminal/Postman showing JSON response
- [ ] Save as: `screenshot_3_api_response.png`

### **Screenshot 4: Architecture Diagram**

- [ ] View: `workshop_aws-main/static/images/5-Workshop/overview/architecture.png`
- [ ] Verify it shows complete pipeline
- [ ] **Screenshot:** Updated architecture diagram
- [ ] Save as: `screenshot_4_architecture.png`

---

## 📁 Files to Submit

### **Code Files** (Create these in `aws/` folder)
- [ ] `aws/register_model.py` ✅ Created
- [ ] `aws/deploy_endpoint.py` ✅ Created
- [ ] `aws/setup_dynamodb.py` ✅ Created
- [ ] `aws/lambda_handler.py` ✅ Created

### **Documentation Files** (Create in root)
- [ ] `QUICK_START.md` ✅ Created
- [ ] `DEPLOYMENT_GUIDE.md` ✅ Created
- [ ] `IMPLEMENTATION_SUMMARY.md` ✅ Created
- [ ] `SUBMISSION_CHECKLIST.md` (this file) ✅ Created

### **Screenshots** (Create `screenshots/` folder)
- [ ] `screenshots/screenshot_1_endpoint.png`
- [ ] `screenshots/screenshot_2_lambda_test.png`
- [ ] `screenshots/screenshot_3_api_response.png`
- [ ] `screenshots/screenshot_4_architecture.png`

### **Updated Project Files**
- [ ] `workshop_aws-main/static/images/5-Workshop/overview/architecture.png` (updated)
- [ ] `changeslog.txt` (updated with Phase 4-5)

---

## 🔍 Pre-Submission Verification

```bash
# 1. Check all files exist
ls -la aws/register_model.py
ls -la aws/deploy_endpoint.py
ls -la aws/setup_dynamodb.py
ls -la aws/lambda_handler.py
ls -la QUICK_START.md
ls -la DEPLOYMENT_GUIDE.md

# 2. Verify AWS resources
aws sagemaker list-model-packages --model-package-group-name SCADA-Fault-Prediction

aws sagemaker describe-endpoint --endpoint-name scada-fault-prediction-endpoint

aws dynamodb describe-table --table-name scada-predictions-cache

aws lambda get-function --function-name scada-fault-prediction-api

# 3. Test API one more time
curl -X POST "YOUR_API_ENDPOINT/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": {...}}'
```

---

## 📝 Submission Package

Create a folder with:
```
submission/
├── code/
│   ├── register_model.py
│   ├── deploy_endpoint.py
│   ├── setup_dynamodb.py
│   └── lambda_handler.py
├── docs/
│   ├── QUICK_START.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── SUBMISSION_CHECKLIST.md
└── screenshots/
    ├── screenshot_1_endpoint.png
    ├── screenshot_2_lambda_test.png
    ├── screenshot_3_api_response.png
    └── screenshot_4_architecture.png
```

---

## 🎯 Submission Checklist Summary

### **Code Quality**
- [ ] All 4 Python files created
- [ ] Code is production-ready
- [ ] Comments explain key sections
- [ ] Error handling implemented

### **Functionality**
- [ ] Model registry working
- [ ] Endpoint deployed and InService
- [ ] DynamoDB cache created
- [ ] Lambda function working
- [ ] API Gateway responding

### **Documentation**
- [ ] QUICK_START.md complete
- [ ] DEPLOYMENT_GUIDE.md complete
- [ ] IMPLEMENTATION_SUMMARY.md complete
- [ ] Code comments clear

### **Evidence**
- [ ] 4 screenshots captured
- [ ] Endpoint status verified
- [ ] Lambda test successful
- [ ] API response working

### **Git**
- [ ] All changes committed
  ```bash
  git add .
  git commit -m "Add production ML pipeline: model registry, endpoint, lambda, API"
  git push
  ```

---

## ⏱️ Timeline

| Time | Task | Status |
|------|------|--------|
| **Today** | Read guides + setup | ⏳ DO THIS |
| **Tomorrow AM** | Run training | ⏳ PHASE 1 |
| **Tomorrow 10:00** | Register model | ⏳ PHASE 1 |
| **Tomorrow 10:05** | Setup DynamoDB | ⏳ PHASE 2 |
| **Tomorrow 10:10** | Deploy endpoint | ⏳ PHASE 3 (wait 15 min) |
| **Tomorrow 10:30** | Create Lambda | ⏳ PHASE 4 |
| **Tomorrow 10:35** | Create API Gateway | ⏳ PHASE 4 |
| **Tomorrow 10:45** | Test & screenshot | ⏳ VERIFICATION |
| **Tomorrow 10:50** | Git commit & push | ⏳ FINAL |
| **Tomorrow 11:00** | **READY TO SUBMIT** | ✅ DONE |

---

## 🆘 If Something Goes Wrong

### **Endpoint stuck in "Creating" for > 15 min**
```bash
# Check logs
aws logs tail /aws/sagemaker/Endpoints/scada-fault-prediction-endpoint --follow

# If failed, delete and retry
aws sagemaker delete-endpoint --endpoint-name scada-fault-prediction-endpoint
python aws/deploy_endpoint.py
```

### **Lambda timeout**
```bash
# Increase timeout to 60s
# AWS Lambda Console → Configuration → General → Timeout
```

### **Permission denied errors**
```bash
# Check role has required permissions
aws iam list-attached-role-policies --role-name SageMakerExecutionRole-MLOps
```

### **Model not found in registry**
```bash
# Verify model was approved
aws sagemaker list-model-packages --model-package-group-name SCADA-Fault-Prediction
```

---

## ✅ Final Checklist

Before submitting, verify:

- [ ] **Code**: All 4 files created ✅
- [ ] **Endpoint**: Status = `InService` ✅
- [ ] **Lambda**: Test = `200 OK` ✅
- [ ] **API**: Curl response = valid JSON ✅
- [ ] **Screenshots**: 4 images captured ✅
- [ ] **Docs**: 4 markdown files created ✅
- [ ] **Git**: Changes committed & pushed ✅

---

## 🎉 Ready to Go!

**Start here:**
```bash
cd C:\Hanh\GITHUB\T1_AD
python aws/processing_job.py && python aws/training_job.py
```

**Then follow QUICK_START.md**

**Questions? Check DEPLOYMENT_GUIDE.md**

**Need overview? Read IMPLEMENTATION_SUMMARY.md**

---

**⏰ GOOD LUCK! You've got this!** 🚀
