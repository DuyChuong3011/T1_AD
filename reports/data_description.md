# Mô tả dữ liệu — T1.csv (Wind Turbine SCADA)

## Tổng quan
Dữ liệu SCADA thật của một tuabin gió, năm 2018, lấy mẫu mỗi 10 phút. Bài toán: **phát hiện bất thường không giám sát** (dữ liệu không có nhãn).

- Số bản ghi gốc: 50.530
- Khoảng thời gian: 2018-01-01 → 2018-12-31
- Số mốc đầy đủ theo lưới 10 phút cả năm: 52.560 → **thiếu ~2.030 mốc** (gap thời gian thật)
- Không có ô NaN trong các dòng hiện có, nhưng có dòng thời gian bị thiếu (lộ ra sau khi reindex về lưới đều)

## Các cột
| Cột | Ý nghĩa | Khoảng giá trị |
|-----|---------|----------------|
| `Date/Time` | Mốc thời gian (định dạng `%d %m %Y %H:%M`) | 2018 |
| `LV ActivePower (kW)` | Công suất thực tuabin phát ra | -2.47 → 3618.73 |
| `Wind Speed (m/s)` | Tốc độ gió đo tại trạm | 0 → 25.21 |
| `Theoretical_Power_Curve (KWh)` | Công suất kỳ vọng theo đường cong nhà sản xuất | 0 → 3600 |
| `Wind Direction (°)` | Hướng gió (góc tuần hoàn 0–360) | 0 → 360 |

## Hướng tiếp cận (không giám sát)
Vì không có nhãn `is_anomaly`, ta không thể phân loại có giám sát. Hai hướng chính:

1. **Phần dư đường cong công suất**: `residual = LV ActivePower − Theoretical_Power_Curve`. Điểm có phần dư âm lớn (tuabin phát ít hơn hẳn mức đáng lẽ đạt được ở tốc độ gió đó) là ứng viên bất thường. Dùng ngưỡng Z-score trên phần dư để gắn cờ.
2. **Mô hình không giám sát** trên bộ đặc trưng: Isolation Forest, LOF, One-Class SVM, autoencoder.

## Pipeline xử lý
1. `load_data`: parse thời gian, sắp xếp, reindex về lưới 10 phút (lộ gap thành NaN).
2. Điền khuyết: nội suy tuyến tính (`interpolate`).
3. Ngoại lai: phát hiện IQR/Z-score; cap nhẹ (thận trọng vì là dữ liệu cần phát hiện bất thường).
4. Kỹ thuật đặc trưng: rolling mean/std (cửa sổ 6, 24), z-score, sai phân bậc 1 + đặc trưng `power_residual`.
5. Chia train/test **theo thời gian** (70/30, không xáo trộn).
6. Chuẩn hóa Z-score: fit trên train, transform test (tránh rò rỉ dữ liệu).

## Đầu ra
- `data/processed/T1_processed.csv` — bảng đặc trưng đầy đủ (chưa scale).
- `data/features/T1_train.csv`, `data/features/T1_test.csv` — train/test đã chuẩn hóa.
- `reports/figures/` — biểu đồ EDA (power curve, residual, phân phối, tương quan, đặc trưng trượt).
