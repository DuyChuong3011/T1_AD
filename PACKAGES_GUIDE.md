# 📦 Packages Guide - Cần gì cho cái gì

---

## 🎯 Quick Install

```powershell
# Production only
pip install -r requirements.txt

# Production + Development
pip install -r requirements-dev.txt
```

---

## 📋 Core ML Packages

### **pandas** (data processing)
```python
import pandas as pd
df = pd.read_csv('data.csv')
df['new_col'] = df['col'] * 2
```
- Dùng cho: Đọc/xử lý CSV, dataframe operations
- Tại: `src/preprocessing.py`, `src/feature_engineering.py`

### **numpy** (numerical computing)
```python
import numpy as np
arr = np.array([1, 2, 3])
mean = np.mean(arr)
```
- Dùng cho: Mathematical operations, arrays
- Tại: `src/train.py`, `demo/verify_with_raw_data.py`

### **scikit-learn** (machine learning)
```python
from sklearn.mixture import GaussianMixture
model = GaussianMixture(n_components=5)
model.fit(X_train)
```
- Dùng cho: Training GMM model, metrics
- Tại: `src/train.py`, `src/evaluate.py`

### **joblib** (model persistence)
```python
import joblib
joblib.dump(model, 'model.joblib')
loaded_model = joblib.load('model.joblib')
```
- Dùng cho: Save/load model files
- Tại: `src/train.py`, `demo/api.py`

---

## ☁️ AWS Packages

### **boto3** (AWS SDK)
```python
import boto3
s3 = boto3.client('s3')
s3.upload_file('file.csv', 'bucket', 'key')
```
- Dùng cho: S3 operations, AWS interactions
- Tại: `aws/processing_job.py`, `aws/training_job.py`

### **sagemaker** (AWS SageMaker)
```python
from sagemaker.sklearn.processing import SKLearnProcessor
processor = SKLearnProcessor(...)
processor.run(...)
```
- Dùng cho: SageMaker training/processing jobs
- Tại: `aws/processing_job.py`, `aws/training_job.py`

---

## 📊 Visualization Packages

### **matplotlib** (basic plots)
```python
import matplotlib.pyplot as plt
plt.plot(x, y)
plt.show()
```
- Dùng cho: Basic charts (histograms, line plots)
- Tại: `scripts/generate_plots.py`

### **seaborn** (statistical visualization)
```python
import seaborn as sns
sns.heatmap(corr_matrix)
```
- Dùng cho: Heatmaps, distribution plots
- Tại: `notebooks/01_EDA.ipynb`

### **plotly** (interactive charts)
```python
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(...))
```
- Dùng cho: Interactive web charts, web UI
- Tại: `demo/api.py`, `demo/streamlit_app.py`

---

## 🌐 Web API Packages

### **fastapi** (web framework)
```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/predict")
async def predict(data: dict):
    return {"result": "..."}
```
- Dùng cho: Create REST API endpoint
- Tại: `demo/api.py`

### **uvicorn** (ASGI server)
```bash
uvicorn demo.api:app --port 8000
```
- Dùng cho: Run FastAPI server
- Tại: Terminal command

### **python-multipart** (file upload)
```python
from fastapi import File, UploadFile

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
```
- Dùng cho: Handle file uploads in FastAPI
- Tại: `demo/api.py`

---

## 🛠️ Development Packages

### **black** (code formatter)
```bash
black src/
```
- Dùng cho: Auto-format Python code
- Tại: Dev workflow

### **flake8** (code linter)
```bash
flake8 src/
```
- Dùng cho: Check code style
- Tại: Dev workflow

### **pytest** (testing)
```bash
pytest tests/
```
- Dùng cho: Run unit tests
- Tại: Dev workflow

### **mypy** (type checker)
```bash
mypy src/
```
- Dùng cho: Check type hints
- Tại: Dev workflow

### **bandit** (security checker)
```bash
bandit -r src/
```
- Dùng cho: Scan for security issues
- Tại: Dev workflow

---

## 📝 Package Versions Explanation

### Production (requirements.txt)
```
pandas==2.3.3           # Exact version for stability
scikit-learn==1.3.0     # Specific version (model compatibility)
fastapi==0.139.0        # Latest stable
```

**Tại sao cần exact version?**
- Đảm bảo model trained với 1 version sẽ work với cùng version
- Tránh breaking changes

### Development (requirements-dev.txt)
```
black==23.12.0          # Format/lint tools
pytest==7.4.3           # Testing
```

**Tại sao separate?**
- Không cần deploy dev tools lên production
- Nhẹ hơn khi upload AWS

---

## 📊 Installation Summary

| Situation | Command | Ghi Chú |
|-----------|---------|--------|
| **First time setup** | `pip install -r requirements.txt` | Production only |
| **Development** | `pip install -r requirements-dev.txt` | Includes dev tools |
| **Using script** | `.\install.ps1` | Interactive install |
| **Single package** | `pip install pandas==2.3.3` | Install one at a time |

---

## 🔍 Verify Installation

```powershell
# Check all packages
pip list

# Check specific package
pip show pandas

# Test imports
python -c "import pandas, numpy, sklearn; print('✅ OK')"

# Verify key packages
python
>>> import pandas as pd
>>> import numpy as np
>>> import sklearn
>>> from sklearn.mixture import GaussianMixture
>>> import joblib
>>> import fastapi
>>> print('✅ All imports successful')
```

---

## 🚨 Common Issues

### "No module named 'pandas'"
```powershell
# pip install failed or not installed
pip install pandas==2.3.3
```

### "Module 'sklearn' has no attribute 'xxx'"
```powershell
# Wrong scikit-learn version
pip install scikit-learn==1.3.0 --upgrade
```

### "ImportError: cannot import name 'GaussianMixture'"
```powershell
# Version mismatch - reinstall exact version
pip uninstall scikit-learn -y
pip install scikit-learn==1.3.0
```

---

## 💡 Best Practices

### ✅ DO:
- Use `requirements.txt` for production
- Use `requirements-dev.txt` for development
- Pin exact versions for stability
- Regularly update packages

### ❌ DON'T:
- Use `pip install` without version pinning on production
- Mix different scikit-learn versions
- Deploy with dev packages (too heavy)
- Forget to commit requirements.txt

---

## 📦 Size Reference

| Package | Size |
|---------|------|
| pandas | ~50 MB |
| numpy | ~100 MB |
| scikit-learn | ~150 MB |
| boto3 + sagemaker | ~50 MB |
| fastapi | ~5 MB |
| plotly | ~30 MB |
| **Total (all)** | **~400-500 MB** |

---

## 🚀 Quick Install Commands

```powershell
# Option 1: Using script (recommended)
.\install.ps1

# Option 2: Manual production
pip install -r requirements.txt

# Option 3: Manual development
pip install -r requirements-dev.txt

# Option 4: Minimal (just ML)
pip install pandas numpy scikit-learn joblib boto3
```

**Chạy cái nào thoải mái!** 👍
