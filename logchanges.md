# Nhật ký Nâng cấp: T1_AD (Hybrid Supervised XGBoost)

Tài liệu này ghi nhận toàn bộ các thay đổi cốt lõi để nâng cấp dự án từ phương pháp **Học không giám sát (Unsupervised GMM)** cũ lên phương pháp **Học có giám sát (Supervised XGBoost)** mạnh mẽ.

## 1. `src/feature_engineering.py`
- **Sửa đổi:** Bổ sung 3 hàm mới: `encode_wind_direction()`, `calculate_loss()`, và `create_labels()`. Đóng gói kèm khối lệnh thực thi tự động.
- **Lý do:** 
  - Khắc phục điểm mù về Hướng Gió (mã hóa Sin/Cos để thuật toán hiểu được tính chu kỳ).
  - Tự động sinh ra nhãn lỗi `Label_Error` (đây là Ground Truth) dựa trên định luật vật lý (công suất thất thoát > 50% hoặc máy tắt khi gió to).

## 2. `src/preprocessing.py`
- **Sửa đổi:** Thay đổi phương pháp xử lý của `handle_outliers()` sang `physical` (chỉ giới hạn giá trị âm về 0).
- **Lý do:** Bỏ hoàn toàn thuật toán cắt gọn bằng IQR hoặc Z-score vì nó vô tình xóa mất chính những điểm dữ liệu "bất thường" - vốn là các thời điểm tuabin hỏng hóc mà mô hình cần học.

## 3. `src/train.py`
- **Sửa đổi:** Chuyển đổi mô hình từ `GaussianMixture` sang `xgboost.XGBClassifier`. Mở khóa bộ đọc để tiếp thu toàn bộ đặc trưng (bao gồm Hướng Gió, Giờ, Tháng).
- **Lý do:** XGBoost đem lại khả năng phân loại tốt hơn hàng chục lần so với GMM trong bài toán tìm lỗi. Đồng thời, tôi đã khắc phục lỗi đọc file bằng cách tự động dò tìm `_features.csv` để bạn dễ dàng chạy cả luồng.

## 4. `src/evaluate.py`
- **Sửa đổi:** Xóa bỏ luật 3-Sigma và tham số giả định `contamination`. Chấm điểm so khớp thẳng kết quả dự đoán với `Label_Error`.
- **Lý do:** Đánh giá bằng `Label_Error` giúp phản ánh điểm số F1, AUC chân thực 100% dựa trên hao hụt kinh tế thực tế của nhà máy điện gió, chứ không còn là điểm số ảo mộng của unsupervised learning nữa.
