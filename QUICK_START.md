# ⚡ QUICK START - 30 Min Deployment

**Cho những người nộp ngày mai - đọc cái này thôi!**

---

## 📌 Điều gì vừa được thêm vào?

```
aws/
├── register_model.py         ← Register model to Model Registry
├── lambda_handler.py         ← Prediction API (copy vào Lambda console)
├── deploy_endpoint.py        ← Auto-deploy endpoint
└── setup_dynamodb.py         ← Cache table setup

DEPLOYMENT_GUIDE.md           ← Chi tiết step-by-step
```

---

## 🚀 Deploy in 4 Commands

```bash
cd C:\Hanh\GITHUB\T1_AD

# 1. Run training (5 min)
python aws/processing_job.py
python aws/training_job.py

# 2. Register model (1 min)
python aws/register_model.py \
  --training-job-name "YOUR_TRAINING_JOB_NAME_HERE" \
  --model-version "v1.0" \
  --approve

# 3. Setup cache (2 min)
python aws/setup_dynamodb.py

# 4. Deploy endpoint (10 min)
python aws/deploy_endpoint.py --instance-type "ml.m5.xlarge" --instance-count 1
```

**Then:** Setup Lambda + API Gateway manually (5 min) → See DEPLOYMENT_GUIDE.md

---

## 🎯 What Each File Does

### `register_model.py`
```python
# Registers trained model to SageMaker Model Registry
# Supports versioning & approval workflow
# Allows automatic deployment
```

**Usage:**
```bash
python aws/register_model.py \
  --training-job-name "t1-ad-xgboost-20240730-123456" \
  --model-version "v1.0" \
  --approve
```

---

### `deploy_endpoint.py`
```python
# Deploys model from Model Registry to SageMaker Endpoint
# Supports auto-scaling, monitoring, multi-instance
```

**Usage:**
```bash
python aws/deploy_endpoint.py \
  --instance-type "ml.m5.xlarge" \
  --instance-count 1
```

**Output:** `scada-fault-prediction-endpoint` ready for inference

---

### `setup_dynamodb.py`
```python
# Creates DynamoDB table for prediction caching
# TTL: 1 hour (auto-delete expired items)
# Cost: ~FREE (pay-per-request)
```

**Usage:**
```bash
python aws/setup_dynamodb.py
```

**Table:** `scada-predictions-cache`

---

### `lambda_handler.py`
```python
# Lambda function handler for prediction API
# Features:
#   - Parse API Gateway events
#   - Call SageMaker endpoint
#   - Cache predictions in DynamoDB
#   - Send metrics to CloudWatch
#   - Error handling

# NOT a script - copy this into AWS Lambda console!
```

**Steps:**
1. Go to AWS Lambda console
2. Create function: `scada-fault-prediction-api`
3. Paste entire `lambda_handler.py` code
4. Set environment variables
5. Set timeout to 60s
6. Deploy

---

## 📊 Architecture After Deployment

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │ HTTPS
       ▼
┌──────────────────────┐
│  API Gateway         │
│  /prod/predict POST  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Lambda Function     │
│  (Check DynamoDB)    │
└──────┬───────────────┘
       │
       ├─→ (Cache hit) → Return cached
       │
       └─→ (Cache miss) → Call Endpoint
                              │
                              ▼
                         ┌──────────────┐
                         │   SageMaker  │
                         │   Endpoint   │
                         │  (ml.m5...)  │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │  DynamoDB    │
                         │  (Cache 1h)  │
                         └──────────────┘
```

---

## ⏰ Timeline

| Step | Task | Duration | Status |
|------|------|----------|--------|
| 1 | Data Processing | 3-5 min | ✅ AUTO |
| 2 | Training Job | 5-10 min | ✅ AUTO |
| 3 | Register Model | 1 min | ✅ AUTO |
| 4 | Setup DynamoDB | 2 min | ✅ AUTO |
| 5 | Deploy Endpoint | 10-15 min | ✅ AUTO |
| 6 | Create Lambda | 3-5 min | 🔧 MANUAL |
| 7 | Create API Gateway | 2-3 min | 🔧 MANUAL |
| 8 | Test API | 2 min | ✅ AUTO |
| **TOTAL** | | **~30-40 min** | ✅ READY |

---

## 🔍 Quick Verification

```bash
# 1. Check model in registry
aws sagemaker list-model-packages \
  --model-package-group-name SCADA-Fault-Prediction

# 2. Check endpoint status
aws sagemaker describe-endpoint \
  --endpoint-name scada-fault-prediction-endpoint | jq .EndpointStatus

# 3. Check DynamoDB table
aws dynamodb describe-table \
  --table-name scada-predictions-cache | jq .Table.TableStatus

# 4. Test Lambda invocation
aws lambda invoke \
  --function-name scada-fault-prediction-api \
  /tmp/test.json
```

---

## 💡 Key Features

✅ **Production Ready**
- Auto-scaling (1-4 instances)
- Prediction caching (reduce cost)
- CloudWatch monitoring
- Error handling

✅ **Well-Architected**
- Model versioning
- Approval workflow
- Infrastructure as Code ready
- Cost optimized

✅ **Scalable**
- Serverless Lambda
- Managed SageMaker Endpoint
- On-demand DynamoDB
- No infrastructure to maintain

---

## 🆘 Troubleshooting

**"Training job not found"**
```bash
# Find your training job name
aws sagemaker list-training-jobs --sort-order Descending | jq '.TrainingJobSummaries[0].TrainingJobName'
```

**"Model not approved"**
```bash
# Approve manually
python aws/register_model.py \
  --training-job-name "YOUR_JOB_NAME" \
  --approve
```

**"Endpoint still creating"**
```bash
# Wait up to 15 minutes
# Monitor: aws sagemaker describe-endpoint --endpoint-name scada-fault-prediction-endpoint
```

**"Lambda timeout"**
- Increase timeout to 60s in Lambda console
- Configuration → General → Timeout

---

## 📝 What to Submit Tomorrow

1. **Code files:**
   - ✅ `aws/register_model.py`
   - ✅ `aws/lambda_handler.py`
   - ✅ `aws/deploy_endpoint.py`
   - ✅ `aws/setup_dynamodb.py`

2. **Documentation:**
   - ✅ `DEPLOYMENT_GUIDE.md` (detailed steps)
   - ✅ `QUICK_START.md` (this file)

3. **Architecture:**
   - ✅ `workshop_aws-main/static/images/5-Workshop/overview/architecture.png` (updated)

4. **Proof of working:**
   - 📸 Screenshot of:
     - [ ] Endpoint `InService`
     - [ ] Lambda test success
     - [ ] API Gateway response

---

## 🎯 Key Takeaways

**Before:** Manual ML deployment
- Ad-hoc training
- Manual endpoint deployment
- No versioning
- Hard to reproduce

**After:** Production ML pipeline
- Automated training
- Model Registry versioning
- One-command deployment
- Fully reproducible
- Cost optimized (cache + scaling)

---

## 📊 Architecture Improvements (After Submission)

For future enhancements:

1. **Add CloudFront** - CDN caching
2. **Add VPC** - Network isolation
3. **Add X-Ray** - Distributed tracing
4. **Add CI/CD** - GitHub Actions
5. **Add Monitoring** - Model drift detection

See: `DEPLOYMENT_GUIDE.md` for detailed next steps

---

## ✅ Checklist Before Submission

- [ ] Training job completed
- [ ] Model registered in Model Registry
- [ ] Model approved
- [ ] DynamoDB table created with TTL enabled
- [ ] Endpoint deployed and `InService`
- [ ] Lambda function created and tested
- [ ] API Gateway endpoint working
- [ ] Tested prediction via API
- [ ] Screenshots taken
- [ ] Code committed to git

---

**🚀 Ready to deploy? Start with:**
```bash
python aws/processing_job.py && python aws/training_job.py
```

**Then check: DEPLOYMENT_GUIDE.md for detailed steps**
