# Nhật ký Nâng cấp: T1_AD (Hybrid Supervised Version)

Tài liệu này ghi nhận các thay đổi cốt lõi để nâng cấp dự án từ **Học không giám sát (Unsupervised GMM)** lên **Học có giám sát (Supervised XGBoost)**.

## 1. `src/feature_engineering.py`
- **Sửa đổi:** Thêm 3 hàm mới: `encode_wind_direction()`, `calculate_loss()`, và `create_labels()`.
- **Lý do:** 
  - Khắc phục điểm mù về Hướng Gió (chuyển sang Sin/Cos để máy học dễ hiểu chu kỳ).
  - Định nghĩa lại Lỗi dựa trên vật lý thực tế (Hao hụt > 50% hoặc gió to mà máy tắt) thông qua việc tự động sinh ra cột `Label_Error`. Việc có Nhãn là điều kiện tiên quyết để chạy XGBoost.

## 2. `src/preprocessing.py`
- **Sửa đổi:** Sửa logic của hàm `handle_outliers()` sang phương pháp `physical` (chỉ đưa các giá trị âm về 0).
- **Lý do:** Ở bản cũ, thuật toán thống kê (IQR/Z-score) đã vô tình "gọt" mất các điểm dữ liệu bất thường (vốn chính là thời điểm máy hỏng). Việc chuyển sang lọc vật lý giúp bảo toàn 100% bằng chứng hỏng hóc để AI học tập.

## 3. `src/train.py`
- **Sửa đổi:** 
  - Thay thế thuật toán `GaussianMixture` bằng `XGBClassifier`.
  - Mở khóa bộ lọc tính năng (nạp toàn bộ đặc trưng thay vì chỉ lấy cột có tên `zscore` và `diff`).
- **Lý do:** XGBoost mang lại độ chính xác cao hơn rất nhiều và dễ kiểm soát hơn. Việc mở khóa tính năng giúp XGBoost hấp thụ được các dữ liệu giá trị như Hướng Gió, Tháng, Giờ.

## 4. `src/evaluate.py`
- **Sửa đổi:** Loại bỏ logic tự động sinh Pseudo-label (Quy tắc 3-Sigma) và xóa bỏ tham số `contamination` (1.5%). Thay vào đó dùng trực tiếp cột `Label_Error` để chấm điểm.
- **Lý do:** Đánh giá bằng Pseudo-label sinh ra điểm số "ảo". Việc so sánh trực tiếp dự đoán của XGBoost với `Label_Error` (Ground Truth) mang lại các chỉ số F1, AUC, Precision thực tế, phản ánh chính xác bài toán kinh tế của nhà máy điện gió.
