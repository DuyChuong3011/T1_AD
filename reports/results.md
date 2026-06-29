# Kỹ thuật xử lý và phân tích kết quả — Phát hiện bất thường không giám sát trên T1.csv

Tài liệu mô tả các kỹ thuật được sử dụng ở từng bước (EDA, tiền xử lý, kỹ thuật đặc trưng) kèm kết quả thu được, trên dữ liệu SCADA tuabin gió `T1.csv` (năm 2018, lấy mẫu 10 phút, 5 cột: thời gian, công suất thực, tốc độ gió, công suất lý thuyết, hướng gió). Dữ liệu không có nhãn nên mục tiêu là mô hình hóa trạng thái vận hành bình thường và khoanh vùng các điểm lệch để phục vụ phát hiện bất thường không giám sát.

## 1. Đưa về lưới thời gian đều và xử lý khuyết

**Kỹ thuật.** Hàm `load_data` parse cột `Date/Time` (định dạng `%d %m %Y %H:%M`), sắp xếp tăng dần theo thời gian, loại mốc trùng, rồi **reindex về lưới đều 10 phút** cho toàn năm 2018. Mục đích là làm lộ các mốc thời gian bị thiếu — vốn là gián đoạn thật của hệ SCADA — thành ô NaN. Sau đó dùng `handle_missing_values` với chiến lược **nội suy tuyến tính** (`interpolate`), bổ sung `ffill`/`bfill` để lấp hai đầu chuỗi. Nội suy được chọn thay cho điền trung bình vì phù hợp với bản chất chuỗi thời gian liên tục.

**Kết quả.** Dữ liệu gốc 50.530 bản ghi; lưới đầy đủ là 52.560 mốc, tức **thiếu 2.030 mốc (3,86%)**. Sau nội suy, không còn giá trị khuyết nào. Đây là điểm khác biệt rõ so với dữ liệu mô phỏng (vốn sạch hoàn hảo): ở đây bước xử lý khuyết thực sự có tác dụng và phản ánh đúng đặc thù dữ liệu vận hành thực tế.

## 2. Phát hiện và xử lý ngoại lai

**Kỹ thuật.** Phát hiện ngoại lai bằng hai phương pháp để đối chiếu: **IQR** (ngoài khoảng [Q1 − 1,5·IQR, Q3 + 1,5·IQR]) và **Z-score** (|z| > 3,0). Việc xử lý dùng phương pháp **cap (clip về biên IQR)** ở mức thận trọng — vì trong bài toán phát hiện bất thường, điểm "ngoại lai" chính là đối tượng cần giữ, không được loại bỏ.

**Kết quả.** Tỷ lệ ngoại lai rất thấp: chỉ `Wind Speed` có ~0,5–0,6%, ba biến còn lại gần như 0%.

| Cột | % ngoại lai (IQR) | % ngoại lai (Z-score) |
|-----|-------------------|------------------------|
| LV ActivePower (kW) | 0,00 | 0,00 |
| Wind Speed (m/s) | 0,64 | 0,47 |
| Theoretical_Power_Curve (KWh) | 0,00 | 0,00 |
| Wind Direction (°) | 0,00 | 0,00 |

Điều này cho thấy biên độ giá trị nằm trong dải hợp lý; tín hiệu bất thường ở đây không nằm ở "giá trị cực trị từng biến" mà ở **quan hệ giữa công suất và tốc độ gió** (mục 4).

## 3. Phân tích tương quan và phân phối

**Kỹ thuật.** Tính ma trận tương quan Pearson giữa bốn biến số và vẽ histogram + KDE cho từng biến (`figures/correlation_matrix.png`, `figures/distributions.png`).

**Kết quả.** Công suất thực tương quan rất mạnh với tốc độ gió (r = 0,909) và với công suất lý thuyết (r = 0,942). Quan hệ chặt này khẳng định đường cong công suất là cơ sở hợp lý để mô hình hóa hành vi bình thường: ở mỗi mức gió, công suất kỳ vọng gần như xác định, nên sai lệch lớn so với kỳ vọng là tín hiệu bất thường đáng tin cậy.

## 4. Đường cong công suất và phần dư (cốt lõi của hướng không giám sát)

**Kỹ thuật.** Vẽ scatter công suất thực theo tốc độ gió, phủ đường cong lý thuyết (`figures/power_curve.png`). Định nghĩa đặc trưng miền **`power_residual = LV ActivePower − Theoretical_Power_Curve`**, rồi chuẩn hóa phần dư bằng Z-score và **gắn cờ ứng viên bất thường khi |z| > 3**. Đây là cách phát hiện bất thường không cần nhãn: lấy đường cong lý thuyết làm "kỳ vọng", phần dư lớn = lệch khỏi vận hành bình thường.

**Kết quả.**
- Phần dư có trung bình −203,0 kW, độ lệch chuẩn 459,1 kW, khoảng từ −3600,0 đến +598,7 kW; phân phối lệch âm rõ rệt (trường hợp xấu nhất −3600 kW ứng với kỳ vọng tối đa nhưng sản lượng bằng 0 — tuabin dừng hoàn toàn).
- Ngưỡng |z| > 3 cho **1.469 ứng viên bất thường (2,79%)**, và **100% đều có phần dư âm** — tức toàn bộ là phát ít hơn kỳ vọng, không có trường hợp vượt. Đặc điểm này khớp hoàn hảo với kỳ vọng vật lý của lỗi/suy giảm hiệu suất (`figures/residual_anomaly.png`).
- Theo tri thức miền, số điểm **gió > 3,5 m/s nhưng công suất < 100 kW** (nghi dừng máy/lỗi) lên tới **4.429 (8,43%)** — lớn hơn tập theo ngưỡng Z-score, phản ánh các giai đoạn ngừng vận hành. Tùy mục tiêu (chỉ bắt sự cố nặng hay cả suy giảm nhẹ) có thể chọn tiêu chí khoanh vùng khác nhau.

## 5. Kỹ thuật đặc trưng

**Kỹ thuật.** Trên dữ liệu đã làm sạch, tạo thêm đặc trưng chuỗi thời gian: **trung bình trượt và độ lệch chuẩn trượt** (cửa sổ 6 và 24 mẫu, tức 1 giờ và 4 giờ), **z-score**, và **sai phân bậc 1** (diff) cho ba tín hiệu chính (công suất, tốc độ gió, công suất lý thuyết); kèm đặc trưng miền `power_residual`. `Wind Direction` được giữ nguyên, không đưa vào phép trượt vì là đại lượng góc tuần hoàn (trung bình trượt của góc không có ý nghĩa).

**Kết quả.** Số cột tăng từ 5 lên **24**. Các đặc trưng trượt bắt được xu hướng và độ biến động (ví dụ độ lệch chuẩn trượt tăng vọt quanh các sự kiện), diff bắt thay đổi tức thời — đều là tín hiệu hữu ích cho mô hình phát hiện bất thường (`figures/rolling_features.png`).

## 6. Chia dữ liệu và chuẩn hóa

**Kỹ thuật.** Do không có nhãn, dùng **chia theo thời gian** (`split_train_test_chrono`): 70% đầu chuỗi làm train, 30% sau làm test, không xáo trộn để giữ tính liên tục thời gian. **Chuẩn hóa Z-score** được **fit trên train rồi transform sang test** bằng chính tham số của train (tham số `stats`/`return_stats`), nhằm tránh rò rỉ dữ liệu tương lai vào huấn luyện.

**Kết quả.**

| Tập | Số mẫu | Khoảng thời gian |
|-----|--------|------------------|
| Train | 36.792 | 2018-01-01 → 2018-09-13 |
| Test | 15.768 | 2018-09-13 → 2018-12-31 |

Sau chuẩn hóa, trung bình các đặc trưng trên train xấp xỉ 0 (đúng kỳ vọng của standardization), còn test giữ phân phối lệch theo tham số train — không bị rò rỉ.

## 7. Kết luận

Bộ kỹ thuật áp dụng phù hợp với đặc thù dữ liệu thật: reindex + nội suy lấp được gián đoạn thời gian; phát hiện ngoại lai thận trọng để không xóa mất tín hiệu cần tìm; phân tích đường cong công suất + phần dư cho tín hiệu bất thường rõ ràng (khoảng 2,8% theo ngưỡng phần dư, tới 8,4% nếu tính cả giai đoạn dừng máy), tất cả đều theo hướng giảm hiệu suất đúng kỳ vọng vật lý; kỹ thuật đặc trưng và chia/chuẩn hóa không rò rỉ tạo ra bộ dữ liệu sẵn sàng cho mô hình hóa. Các đầu ra `data/processed/T1_processed.csv`, `data/features/T1_train.csv` và `T1_test.csv` đã sẵn sàng.

## 8. Hạn chế và hướng tiếp theo

Vì không có nhãn thật, các con số bất thường là ứng viên theo heuristic (ngưỡng phần dư) và ngưỡng |z| > 3 chỉ là quy ước — chưa thể đánh giá precision/recall chặt chẽ. Dữ liệu cũng chỉ thuộc một tuabin trong một năm nên chưa khái quát. Bước tiếp theo nên huấn luyện mô hình phát hiện bất thường không giám sát (Isolation Forest, Local Outlier Factor, One-Class SVM hoặc autoencoder) trên `T1_train.csv`, chấm điểm trên `T1_test.csv`, rồi đối chiếu chéo kết quả mô hình với ngưỡng phần dư đường cong công suất để kiểm chứng.
