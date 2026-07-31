# SCADA Fault Prediction Platform - AWS MLOps

Dự án Xây dựng hệ thống Học Máy Toàn Trình (End-to-End Machine Learning Pipeline) trên nền tảng **Amazon Web Services (AWS)** để dự đoán và phát hiện sớm các dị thường (Anomaly Detection) từ dữ liệu cảm biến SCADA của Tua-bin điện gió.

## Tổng quan
Trong công nghiệp điện gió, việc phát hiện sớm các sự cố của Tua-bin thông qua dữ liệu SCADA có thể tiết kiệm chi phí bảo trì. Dự án này xây dựng quy trình MLOps tự động hóa từ việc lưu trữ dữ liệu, tiền xử lý, huấn luyện mô hình XGBoost, cho đến khâu tinh chỉnh siêu tham số và đóng gói mô hình.

Mô hình đã được xử lý chống rò rỉ dữ liệu một cách nghiêm ngặt, sử dụng các đặc trưng về tốc độ gió, hướng gió và thời gian để dự đoán sự cố.

## Kiến trúc MLOps
Dự án được thiết kế theo tiêu chuẩn công nghiệp sử dụng các dịch vụ của AWS:
- **Lưu trữ dữ liệu tập trung (Data Lake):** Amazon S3
- **Bảo mật & Phân quyền:** AWS IAM (Roles & Policies)
- **Tiền xử lý dữ liệu (Data Processing):** Amazon SageMaker Processing Jobs
- **Huấn luyện mô hình (Model Training):** Amazon SageMaker Training Jobs
- **Tối ưu hóa siêu tham số (HPO):** Amazon SageMaker HPO / Optuna
- **Triển khai (Deployment):** Amazon SageMaker Endpoints 

## Cấu trúc thư mục

```text
SCADA-Fault-Prediction
 ┣ aws/                # Scripts tương tác trực tiếp với Amazon SageMaker
 ┃ ┣ processing_job.py # Khởi chạy SageMaker Processing Job
 ┃ ┣ training_job.py   # Khởi chạy SageMaker Training Job
 ┃ ┣ hpo.py            # SageMaker Hyperparameter Tuning Job
 ┃ ┗ register_model.py # Đăng ký mô hình lên SageMaker Model Registry
 ┣ src/                # Mã nguồn Machine Learning cốt lõi
 ┃ ┣ preprocessing.py  # Xử lý nhiễu, nội suy, trích xuất đặc trưng
 ┃ ┣ feature_engineering.py # Các hàm tạo đặc trưng và gán nhãn tự động
 ┃ ┣ train.py          # Script huấn luyện dùng chung cho Cloud
 ┃ ┣ evaluate_model.py  # Script đánh giá mô hình  
 ┃ ┣ local_train.py    # Huấn luyện XGBoost cục bộ, tối ưu Threshold và lưu model
 ┃ ┣ local_hpo.py    # Tối ưu siêu tham số bằng Optuna (Time Series CV)
 ┣ data/               # Chứa dữ liệu Raw, Processed, Features (git-ignored)
 ┣ notebooks/          # Jupyter Notebooks dùng để EDA và thử nghiệm thuật toán
 ┣ models/             # Thư mục lưu Model Artifacts (model.tar.gz)
 ┣ scripts/            # Các công cụ hỗ trợ tiện ích
 ┃ ┗ setupS3.py        # Tự động tạo bucket và tải dữ liệu thô lên S3
 ┣ requirements.txt    # Danh sách các thư viện cần thiết
 ┗ README.md           # Tài liệu dự án
```

## Hướng dẫn chạy dự án

### 1. Chuẩn bị Môi trường
Cài đặt thư viện thông qua requirements:
```bash
pip install -r src/requirements.txt
pip install optuna xgboost sagemaker boto3
```

### 2. Thiết lập Đám mây (S3)
Chạy script để khởi tạo bucket trên AWS S3 và tự động đẩy dữ liệu thô `data/raw/T1.csv` lên mây:
```bash
python scripts/setupS3.py
```

### 3. Tiền Xử Lý Dữ Liệu
Bạn có 2 lựa chọn (Local hoặc Cloud):
- **Chạy Local (Cục bộ):** Xử lý dữ liệu ngay trên máy cá nhân để tiết kiệm chi phí/vượt qua giới hạn quota.
  ```bash
  python src/preprocessing.py
  ```
- **Chạy trên AWS SageMaker:**
  ```bash
  python aws/processing_job.py
  ```
Kết quả sinh ra tập `T1_train.csv` và `T1_test.csv` đã được làm sạch, trích xuất Rolling Stats, chuẩn hóa Z-score khắt khe (chống rò rỉ thời gian).

### 4. Huấn luyện Mô hình
Bạn có thể chọn huấn luyện mô hình tại Local hoặc trên Đám mây (AWS SageMaker):
- **Chạy Local (Cục bộ):**
  ```bash
  python src/local_train.py
  ```
  *Ghi chú: Lệnh này sẽ tự động tìm Threshold tốt nhất và đóng gói mô hình thành `models/model.tar.gz`.*
- **Chạy trên AWS SageMaker:**
  ```bash
  python aws/training_job.py
  ```
  *Ghi chú: Tự động cấp phát máy chủ, lấy dữ liệu từ S3, huấn luyện và lưu trực tiếp `model.tar.gz` về lại S3.*

### 5. (Tùy chọn) Tối ưu hóa siêu tham số (HPO)
- **Chạy Local bằng Optuna:**
  ```bash
  python src/local_hpo.py
  ```
- **Chạy trên AWS SageMaker:**
  ```bash
  python aws/hpo.py
  ```

## Kết quả Mô hình (XGBoost)
Sau khi loại bỏ hiện tượng rò rỉ dữ liệu (Data Leakage) từ các biến liên quan đến công suất, mô hình đã đạt hiệu suất thực tế vững chắc trên tập kiểm thử (Test Set - Mùa Đông):
- **Ngưỡng tối ưu (Threshold):** `0.10`
- **ROC-AUC:** `0.7945`
- **F1-Score:** `0.5495`
- **Precision:** `0.6390`
- **Recall:** `0.4819`

Mô hình hiện tại hoàn toàn có khả năng tổng quát hóa, chỉ cần theo dõi các thông số tốc độ gió để đưa ra cảnh báo sớm về các sự cố trồi sụt công suất bất thường.

