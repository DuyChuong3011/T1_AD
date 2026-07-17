# 🚀 Quick AWS Upload - Đã có credentials

Nếu bạn đã có Access Key ID, Secret Access Key, và S3 bucket, chỉ cần làm theo bước này.

---

## 1️⃣ Setup AWS CLI (5 phút)

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Nhập lần lượt:
# AWS Access Key ID: AKIA...xxxx
# AWS Secret Access Key: wJal...xxxx
# Default region: ap-southeast-1
# Default output: json
```

### ✅ Verify setup

```bash
aws sts get-caller-identity
# Output:
# {
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

---

## 2️⃣ Clean Project (2 phút)

```bash
# Xóa những cái không cần upload
rm -rf .venv .venv312 venv
find . -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -f data/raw/*.csv

# Check size
du -sh .
# Expected: 100-500 MB
```

---

## 3️⃣ Upload to S3 (2 phút)

### ✅ Cách 1: Upload toàn bộ project

```bash
# Thay YOUR-BUCKET-NAME bằng tên bucket của bạn
aws s3 sync . s3://YOUR-BUCKET-NAME/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --exclude ".venv*/*" \
  --exclude ".pytest_cache/*" \
  --exclude "*.pyc"

# Verify upload
aws s3 ls s3://YOUR-BUCKET-NAME/code/ --recursive --human-readable --summarize
```

### ✅ Cách 2: Upload specific folders

```bash
# Chỉ upload code
aws s3 sync src/ s3://YOUR-BUCKET-NAME/code/src/
aws s3 sync models/ s3://YOUR-BUCKET-NAME/code/models/
aws s3 sync data/ s3://YOUR-BUCKET-NAME/code/data/
aws s3 sync demo/ s3://YOUR-BUCKET-NAME/code/demo/

# Verify
aws s3 ls s3://YOUR-BUCKET-NAME/code/ --recursive
```

### ✅ Cách 3: Upload as zip (nếu muốn backup)

```bash
# Tạo zip file
cd ..
zip -r turbine-model.zip T1_AD \
  -x "T1_AD/.git/*" \
  "T1_AD/__pycache__/*" \
  "T1_AD/.venv*/*"

# Upload zip
aws s3 cp turbine-model.zip s3://YOUR-BUCKET-NAME/backups/

# Verify
aws s3 ls s3://YOUR-BUCKET-NAME/backups/
```

---

## 4️⃣ Verify Upload (1 phút)

```bash
# Kiểm tra files trong S3
aws s3 ls s3://YOUR-BUCKET-NAME/code/ --recursive

# Kiểm tra size
aws s3 ls s3://YOUR-BUCKET-NAME/code/ --recursive --human-readable --summarize

# Kiểm tra specific file
aws s3 ls s3://YOUR-BUCKET-NAME/code/models/
aws s3 ls s3://YOUR-BUCKET-NAME/code/src/
```

---

## 5️⃣ Next Steps - Train on SageMaker

### ✅ Run training job

```bash
# Update bucket name trong aws/training_job.py
nano aws/training_job.py

# Thay:
# bucket = "YOUR-BUCKET-NAME"
# role = "arn:aws:iam::YOUR-ACCOUNT-ID:role/YOUR-ROLE"

# Run training
python aws/training_job.py \
  --bucket YOUR-BUCKET-NAME \
  --region ap-southeast-1 \
  --role arn:aws:iam::YOUR-ACCOUNT-ID:role/SageMakerRole
```

### ✅ Run processing job

```bash
python aws/processing_job.py \
  --bucket YOUR-BUCKET-NAME \
  --region ap-southeast-1 \
  --role arn:aws:iam::YOUR-ACCOUNT-ID:role/SageMakerRole
```

---

## 📋 One-Liner Commands

### Upload everything

```bash
aws s3 sync . s3://YOUR-BUCKET-NAME/code/ --exclude ".git/*" --exclude "__pycache__/*" --exclude ".venv*/*"
```

### List what's on S3

```bash
aws s3 ls s3://YOUR-BUCKET-NAME/code/ --recursive
```

### Download from S3 (if needed)

```bash
aws s3 sync s3://YOUR-BUCKET-NAME/code/ ./downloaded-code/
```

### Delete from S3

```bash
aws s3 rm s3://YOUR-BUCKET-NAME/code/old-file --recursive
```

---

## 🔍 Troubleshooting

### Error: "Unable to locate credentials"

```bash
# Credentials not configured
aws configure

# Or check credentials file
cat ~/.aws/credentials  # Linux/Mac
type %USERPROFILE%\.aws\credentials  # Windows
```

### Error: "Access Denied"

```bash
# Check if user has S3 permissions
aws iam get-user

# Check bucket access
aws s3 ls s3://YOUR-BUCKET-NAME/

# If denied: Ask admin to add S3 permissions to your IAM user
```

### Error: "NoSuchBucket"

```bash
# List all your buckets
aws s3 ls

# Use correct bucket name
aws s3 ls s3://EXACT-BUCKET-NAME/
```

### Upload very slow

```bash
# Use parallel uploads (faster)
aws s3 sync . s3://YOUR-BUCKET-NAME/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --parallel 10  # Use 10 parallel threads

# Or use --no-follow-symlinks if symlinks exist
```

---

## 📊 Monitoring Upload

### Check upload progress

```bash
# Real-time sync with verbose output
aws s3 sync . s3://YOUR-BUCKET-NAME/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --dryrun  # First test without uploading

# Actual upload
aws s3 sync . s3://YOUR-BUCKET-NAME/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*"
```

### List large files

```bash
aws s3api list-objects-v2 \
  --bucket YOUR-BUCKET-NAME \
  --prefix code/ \
  --query 'Contents[?Size > `10485760`].[Key,Size]' \
  --output table
```

---

## 💾 Before & After Size

### Before (with venv)

```
Total: 2-5 GB
  .venv312: 1.5 GB
  data/raw: 500 MB
  __pycache__: 200 MB
```

### After (clean)

```
Total: 100-500 MB
  src: 50 KB
  models: 50 MB
  data/features: 100 MB
  notebooks: 100 MB
```

---

## 🎯 Recommended Upload Strategy

### Quick (code only)

```bash
# ~50 MB - just code
aws s3 sync src/ s3://YOUR-BUCKET-NAME/code/src/
aws s3 sync demo/ s3://YOUR-BUCKET-NAME/code/demo/
aws s3 sync models/ s3://YOUR-BUCKET-NAME/code/models/
```

### Standard (code + features)

```bash
# ~200 MB - code + processed features
aws s3 sync . s3://YOUR-BUCKET-NAME/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --exclude ".venv*/*" \
  --exclude "data/raw/*"
```

### Full Backup (everything)

```bash
# ~500 MB - everything except venv
zip -r backup.zip . \
  -x ".git/*" "__pycache__/*" ".venv*/*" "data/raw/*"

aws s3 cp backup.zip s3://YOUR-BUCKET-NAME/backups/$(date +%Y%m%d).zip
```

---

## ✅ Final Checklist

```bash
[ ] AWS CLI installed (aws --version)
[ ] Credentials configured (aws sts get-caller-identity)
[ ] Bucket accessible (aws s3 ls s3://YOUR-BUCKET-NAME/)
[ ] Project cleaned (no .venv, __pycache__)
[ ] Files ready to upload (ls -la)
[ ] Dry-run successful (--dryrun option)
[ ] Upload completed (aws s3 ls s3://YOUR-BUCKET-NAME/code/ --recursive)
```

---

## 🚀 TLDR - Just Run This

```bash
# 1. Setup (one time)
pip install awscli
aws configure

# 2. Clean
rm -rf .venv* venv
find . -name __pycache__ -exec rm -rf {} +

# 3. Upload
aws s3 sync . s3://YOUR-BUCKET-NAME/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --exclude ".venv*/*"

# 4. Verify
aws s3 ls s3://YOUR-BUCKET-NAME/code/ --recursive --human-readable --summarize
```

**Done!** 🎉
