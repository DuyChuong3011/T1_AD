# 📋 AWS Upload Checklist

Trước khi upload dự án lên AWS, cần kiểm tra những gì dưới đây.

---

## 🔐 1. SECURITY - Rất Quan Trọng!

### ✅ Kiểm tra Credentials & Secrets

```bash
# Kiểm tra có API keys, passwords trong code không
grep -r "AKIA" .  # AWS Access Key
grep -r "aws_secret" .
grep -r "password" .
grep -r "token" .
```

**Nếu tìm thấy:**
- ❌ KHÔNG upload
- ✅ Move vào `.env` file
- ✅ Add `.env` vào `.gitignore`

### ✅ Tạo `.gitignore`

```bash
# Tạo file .gitignore
cat > .gitignore << 'EOF'
# Environment
.env
.env.local
*.pem
*.key

# Large files
*.tar.gz
*.zip
models/model.joblib
data/raw/*.csv
data/features/*.csv
data/processed/*.csv

# Python
__pycache__/
*.pyc
.venv/
.venv312/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Cache
.cache/
*.log

# Credentials
credentials.json
config.ini
EOF

git add .gitignore
git commit -m "Add .gitignore for security"
```

---

## 📦 2. FILE SIZE - Kiểm tra upload speed

### ✅ Xem size dự án

```bash
# Total size
du -sh .

# Breakdown by folder
du -sh */ | sort -h

# Large files
find . -type f -size +10M
```

**Lưu ý:**
- Model file: `models/model.joblib` (~MB)
- Data files: `data/raw/T1.csv` (~MB)
- Venv: `.venv312/` (nhiều GB) ❌ KHÔNG cần upload!

### ✅ Xóa những cái không cần

```bash
# Xóa venv
rm -rf .venv .venv312 venv

# Xóa cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +

# Xóa large raw data (giữ processed)
rm -f data/raw/*.csv

# Size sau khi clean
du -sh .
```

**Expected size:** 100-500 MB (tùy data)

---

## 📋 3. PROJECT STRUCTURE - AWS expects

### ✅ Cấu trúc tối ưu cho AWS:

```
T1_AD/
├── src/                    # Source code
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train.py
│   └── evaluate.py
├── models/
│   └── model.joblib        # ✅ Giữ model
├── data/
│   ├── processed/          # ✅ Processed data
│   └── features/           # ✅ Features
├── demo/                   # Web UI/API
│   ├── api.py
│   ├── streamlit_app.py
│   └── requirements_demo.txt
├── scripts/
│   ├── train_job.py        # SageMaker training
│   └── processing_job.py   # SageMaker processing
├── .gitignore              # ✅ MUST HAVE
├── requirements.txt        # ✅ Dependencies
├── requirements-dev.txt    # Development
└── README.md              # ✅ Documentation
```

### ✅ AWS-specific files cần add:

```bash
# 1. requirements.txt (production)
cat > requirements.txt << 'EOF'
pandas==2.3.3
numpy==2.3.5
scikit-learn==1.3.0
joblib==1.3.0
boto3==1.28.0
sagemaker==2.150.0
EOF

# 2. AWS SAM template (optional)
cat > template.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Wind Turbine Prediction Model'

Parameters:
  S3Bucket:
    Type: String
    Description: S3 bucket for training data

Resources:
  SageMakerRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: sagemaker.amazonaws.com
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'

Outputs:
  RoleArn:
    Value: !GetAtt SageMakerRole.Arn
EOF

# 3. README.md
cat > README.md << 'EOF'
# 🌬️ Wind Turbine Failure Prediction

## Overview
Anomaly detection model for wind turbine SCADA data using GMM.

## Data
- Source: T1.csv (2018 SCADA data)
- Size: 50K records, 5 features
- Processed: 52K records with features

## Model
- Type: Gaussian Mixture Model (GMM)
- Features: 24 (rolling stats, z-scores, differences)
- Accuracy: AUC 0.93, F1 0.16

## Deploy
### Local
```bash
pip install -r requirements.txt
python src/train.py
```

### AWS SageMaker
```bash
python aws/training_job.py --bucket my-bucket --region ap-southeast-1
```

### API
```bash
pip install -r demo/requirements_demo.txt
uvicorn demo.api:app --port 8000
```
EOF
```

---

## 🔑 4. AWS CREDENTIALS - Setup trước upload

### ✅ Configure AWS CLI

```bash
# Install AWS CLI (if not already)
pip install awscli

# Configure credentials
aws configure

# Nhập:
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: wJal...
# Default region: ap-southeast-1
# Default output: json
```

### ✅ Verify credentials

```bash
aws sts get-caller-identity
# Output:
# {
#   "UserId": "AIDACKCEVSQ6C2EXAMPLE",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

### ⚠️ KHÔNG commit credentials!

```bash
# Check không có credentials trong git
git log -p | grep -i "AKIA\|aws_secret"

# If found:
git filter-branch --tree-filter 'rm -f credentials.json' -- --all
```

---

## ☁️ 5. AWS S3 SETUP - Trước upload

### ✅ Create S3 bucket

```bash
# Create bucket
aws s3 mb s3://my-turbine-project-[timestamp] --region ap-southeast-1

# Verify
aws s3 ls | grep turbine

# Enable versioning (recommended)
aws s3api put-bucket-versioning \
  --bucket my-turbine-project-[timestamp] \
  --versioning-configuration Status=Enabled
```

### ✅ Setup folder structure

```bash
# Create S3 folders
aws s3api put-object --bucket my-turbine-project --key data/
aws s3api put-object --bucket my-turbine-project --key models/
aws s3api put-object --bucket my-turbine-project --key code/
```

### ✅ Upload project

```bash
# Upload code
aws s3 sync . s3://my-turbine-project/code/ \
  --exclude ".git/*" \
  --exclude ".gitignore" \
  --exclude "__pycache__/*" \
  --exclude "*.pyc" \
  --exclude ".venv*" \
  --exclude "venv/*" \
  --exclude ".pytest_cache/*"

# Verify upload
aws s3 ls s3://my-turbine-project/code/ --recursive
```

---

## 🔍 6. PRE-UPLOAD TESTS

### ✅ Run tests locally first

```bash
# Test validation
python demo/verify_with_raw_data.py

# Test API
python -m uvicorn demo.api:app --port 8000

# Test SageMaker script (dry-run)
python aws/training_job.py --dry-run
```

### ✅ Code quality check

```bash
# Install flake8
pip install flake8 black

# Check code style
flake8 src/ --max-line-length=100

# Format code
black src/ --line-length=100

# Check for vulnerabilities
pip install bandit
bandit -r src/
```

---

## 💰 7. COST ESTIMATION

### ✅ Estimate AWS costs

| Service | Usage | Cost/Month |
|---------|-------|-----------|
| SageMaker Training | 10 × ml.m5.large/hour | ~$50 |
| SageMaker Processing | 5 × ml.m5.xlarge/hour | ~$30 |
| S3 Storage | 50 GB | $1.15 |
| EC2 Inference | t3.medium | ~$20 |
| **Total** | | **~$100** |

### ✅ Cost optimization tips

```bash
# Use spot instances (cheaper)
# Use ml.m5.large instead of ml.p3

# Set auto-shutdown
aws ec2 create-instances --instance-type t3.medium \
  --iam-instance-profile Name=MyRole \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=AutoShutdown,Value=true}]'

# Monitor spending
aws ce get-cost-and-usage --time-period ...
```

---

## 📝 8. DOCUMENTATION CHECKLIST

### ✅ Add documentation

- [ ] README.md - Project overview
- [ ] ARCHITECTURE.md - System design
- [ ] DEPLOYMENT.md - How to deploy
- [ ] API.md - API documentation
- [ ] TROUBLESHOOTING.md - Common issues

---

## ✅ FINAL CHECKLIST - Before Upload

```bash
# 1. Security
[ ] No API keys in code
[ ] .gitignore properly set
[ ] credentials in .env (not committed)

# 2. Code quality
[ ] Code formatted (black, flake8)
[ ] Tests pass (validate_model.py)
[ ] No large files (< 100MB)
[ ] No venv folders

# 3. Documentation
[ ] README.md updated
[ ] requirements.txt correct
[ ] Code has comments where needed

# 4. AWS Setup
[ ] AWS CLI configured
[ ] S3 bucket created
[ ] IAM role created
[ ] Region set correctly

# 5. Git
[ ] All changes committed
[ ] No uncommitted files
[ ] Branch clean

# 6. Testing
[ ] Local validation passed
[ ] API tested
[ ] Model predictions verified
```

---

## 🚀 UPLOAD COMMANDS

### ✅ Upload code to S3

```bash
# Clean first
find . -type d -name __pycache__ -exec rm -rf {} +
rm -rf .venv .venv312 venv

# Commit all changes
git add .
git commit -m "Final version for AWS upload"

# Push to GitHub (recommended backup)
git push origin main

# Upload to S3
aws s3 sync . s3://my-turbine-project/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --exclude ".venv*" \
  --exclude "*.pyc" \
  --delete

# Verify
aws s3 ls s3://my-turbine-project/code/ --recursive --human-readable --summarize
```

### ✅ Create deployment package

```bash
# Create zip for SageMaker
cd ..
zip -r turbine-project.zip T1_AD \
  -x "T1_AD/.git/*" \
  "T1_AD/__pycache__/*" \
  "T1_AD/.venv*/*"

# Upload zip
aws s3 cp turbine-project.zip s3://my-turbine-project/packages/

# Verify
aws s3 ls s3://my-turbine-project/packages/
```

---

## 🆘 TROUBLESHOOTING

### Access Denied Error
```bash
# Check permissions
aws s3api head-bucket --bucket my-bucket --region ap-southeast-1

# Fix: Create bucket policy
aws s3api put-bucket-policy --bucket my-bucket \
  --policy file://policy.json
```

### Upload Slow
```bash
# Use multipart upload
aws s3 sync . s3://bucket/ --sse AES256

# Or use parallel uploads
aws s3 cp large-file.zip s3://bucket/ \
  --sse AES256 \
  --expected-size 1GB
```

### Size Too Large
```bash
# Check what's taking space
du -sh */ | sort -rh | head -20

# Remove unnecessary files
rm -rf data/raw/*.csv
rm -rf models/old_models/
```

---

**Bước tiếp theo:** 
1. Hoàn thành checklist
2. Run `verify_with_raw_data.py` (xem model có OK không)
3. Upload lên S3
4. Test trên AWS SageMaker

**Muốn tôi giúp gì không?** 👍
