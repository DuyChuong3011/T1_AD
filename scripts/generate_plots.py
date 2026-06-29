"""
generate_plots.py
=================
Chạy pipeline EDA/tiền xử lý trên T1.csv và xuất các biểu đồ ra reports/figures/.
Bài toán: phát hiện bất thường KHÔNG giám sát (dữ liệu không nhãn).

Cách dùng (từ thư mục T1_AD hoặc bất kỳ):
    python scripts/generate_plots.py
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    src_dir = os.path.join(project_root, "src")
    raw_dir = os.path.join(project_root, "data", "raw")
    fig_dir = os.path.join(project_root, "reports", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    sys.path.insert(0, src_dir)

    import preprocessing as prep
    import feature_engineering as feat

    sns.set_theme(style="whitegrid")

    num_cols = ["LV ActivePower (kW)", "Wind Speed (m/s)",
                "Theoretical_Power_Curve (KWh)", "Wind Direction (°)"]

    print("Đọc & reindex dữ liệu...")
    df = prep.load_data(os.path.join(raw_dir, "T1.csv"))
    df = prep.handle_missing_values(df, columns=num_cols, strategy="interpolate")
    df["power_residual"] = df["LV ActivePower (kW)"] - df["Theoretical_Power_Curve (KWh)"]

    # 1. Đường cong công suất
    print("Vẽ power curve (power_curve.png)...")
    plt.figure(figsize=(10, 7))
    plt.scatter(df["Wind Speed (m/s)"], df["LV ActivePower (kW)"], s=3, alpha=0.2, label="Thực tế")
    order = df["Wind Speed (m/s)"].argsort()
    plt.plot(df["Wind Speed (m/s)"].iloc[order], df["Theoretical_Power_Curve (KWh)"].iloc[order],
             color="red", linewidth=2, label="Lý thuyết")
    plt.xlabel("Tốc độ gió (m/s)"); plt.ylabel("Công suất (kW)")
    plt.title("Đường cong công suất: Thực tế vs Lý thuyết", fontsize=13, fontweight="bold")
    plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "power_curve.png"), dpi=150); plt.close()

    # 2. Phần dư & ứng viên bất thường
    print("Vẽ residual (residual_anomaly.png)...")
    mu, sigma = df["power_residual"].mean(), df["power_residual"].std()
    z = (df["power_residual"] - mu) / sigma
    anom = df[z.abs() > 3]
    fig, axes = plt.subplots(2, 1, figsize=(15, 9))
    sns.histplot(df["power_residual"], bins=80, ax=axes[0], color="slateblue")
    axes[0].axvline(mu + 3 * sigma, color="r", ls="--"); axes[0].axvline(mu - 3 * sigma, color="r", ls="--")
    axes[0].set_title("Phân phối phần dư công suất", fontweight="bold")
    axes[1].plot(df["timestamp"], df["power_residual"], lw=0.4, color="gray")
    axes[1].scatter(anom["timestamp"], anom["power_residual"], color="red", s=8, label="ứng viên bất thường")
    axes[1].set_title("Phần dư theo thời gian & điểm bất thường", fontweight="bold"); axes[1].legend()
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "residual_anomaly.png"), dpi=150); plt.close()

    # 3. Phân phối các biến
    print("Vẽ phân phối (distributions.png)...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10)); axes = axes.flatten()
    for i, col in enumerate(num_cols):
        sns.histplot(data=df, x=col, kde=True, ax=axes[i], color="teal", bins=60)
        axes[i].set_title(col, fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "distributions.png"), dpi=150); plt.close()

    # 4. Ma trận tương quan
    print("Vẽ tương quan (correlation_matrix.png)...")
    plt.figure(figsize=(8, 6))
    sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".3f", vmin=-1, vmax=1, linewidths=0.5)
    plt.title("Tương quan tuyến tính (Pearson)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "correlation_matrix.png"), dpi=150); plt.close()

    # 5. Đặc trưng trượt theo thời gian (1 đoạn)
    print("Vẽ đặc trưng trượt (rolling_features.png)...")
    fe_cols = ["LV ActivePower (kW)", "Wind Speed (m/s)", "Theoretical_Power_Curve (KWh)"]
    dff = feat.calculate_rolling_stats(df, columns=fe_cols, windows=[6, 24])
    sub = dff.iloc[2000:5000]
    fig, ax = plt.subplots(2, 1, figsize=(15, 9), sharex=True)
    ax[0].plot(sub["timestamp"], sub["LV ActivePower (kW)"], alpha=0.4, label="ActivePower")
    ax[0].plot(sub["timestamp"], sub["LV ActivePower (kW)_roll_mean_24"], color="red", lw=1.5, label="Rolling mean 24")
    ax[0].set_title("Công suất & trung bình trượt", fontweight="bold"); ax[0].legend()
    ax[1].plot(sub["timestamp"], sub["LV ActivePower (kW)_roll_std_24"], color="orange", label="Rolling std 24")
    ax[1].set_title("Độ biến động công suất (rolling std)", fontweight="bold"); ax[1].legend()
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "rolling_features.png"), dpi=150); plt.close()

    print(f"Hoàn thành! Đã lưu 5 biểu đồ vào {fig_dir}")


if __name__ == "__main__":
    main()
