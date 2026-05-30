import pandas as pd
import numpy as np
from scipy.stats import ranksums
import os

ALPHA = 0.05
TAU = 0.147
WARMUP_RUNS = 10

def calculate_cliffs_delta(new_samples, base_samples):
    """Đo lường mức độ ảnh hưởng thực tế (Practical Significance)"""
    m, n = len(base_samples), len(new_samples)
    count = 0
    for i in base_samples:
        for j in new_samples:
            if j > i: count += 1
            elif j < i: count -= 1
    return count / (m * n)

def signal_conditioning(df, signature):
    """
    Stage 2: Làm sạch tín hiệu
    - Lọc đúng hàm mục tiêu
    - Xóa 10 mẫu đầu (Warm-up)
    - Lọc ngoại lệ (IQR)
    """
    # 1. Lọc theo chữ ký phương thức (Operation Signature)
    df_filtered = df[df['signature'].str.contains(signature)].copy()
    
    if len(df_filtered) < WARMUP_RUNS + 5:
        return None

    # 2. Tính duration (ms) và loại bỏ Warm-up
    df_filtered['duration'] = (df_filtered['tout'] - df_filtered['tin']) / 1_000_000
    df_steady = df_filtered.iloc[WARMUP_RUNS:].copy()
    
    # 3. Lọc ngoại lệ bằng IQR
    Q1 = df_steady['duration'].quantile(0.25)
    Q3 = df_steady['duration'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    
    S_clean = df_steady[(df_steady['duration'] >= lower) & (df_steady['duration'] <= upper)]
    return S_clean['duration'].values

def process_ppdx(base_path, new_path, target_signature):
    """
    STAGE 3: Định danh sai lệch cục bộ từ file .dat thật
    """
    cols = ['type', 'timestamp', 'signature', 'session', 'trace_id', 'tin', 'tout', 'host', 'index', 'depth']
    
    # Đọc file dữ liệu thô (đối tượng truyền từ Stage 1)
    try:
        df_base_raw = pd.read_csv(base_path, sep=';', names=cols, header=None, on_bad_lines='skip')
        df_new_raw = pd.read_csv(new_path, sep=';', names=cols, header=None, on_bad_lines='skip')
    except Exception as e:
        return f"Lỗi đọc file: {e}"

    # Thực hiện làm sạch (Stage 2)
    S_base = signal_conditioning(df_base_raw, target_signature)
    S_new = signal_conditioning(df_new_raw, target_signature)

    if S_base is None or S_new is None:
        return "Không đủ dữ liệu cho hàm mục tiêu (Check signature!)"

    # Kiểm định Wilcoxon (Stage 3 - Lớp 1)
    stat, p_val = ranksums(S_base, S_new)
    
    # Tính Cliff's Delta (Stage 3 - Lớp 2)
    d = calculate_cliffs_delta(S_new, S_base)
    
    # Tính toán MPD cục bộ (Đối tượng truyền sang Stage 4)
    mpd_local = np.mean(S_new) - np.mean(S_base)
    
    is_regression = (p_val < ALPHA) and (abs(d) >= TAU)

    return {
        "Target": target_signature.split('.')[-1], # Tên hàm rút gọn
        "Samples": len(S_new),
        "P-Value": round(p_val, 5),
        "Cliff-Delta": round(d, 3),
        "MPD_Local (ms)": round(mpd_local, 2),
        "Result": "REGRESSION" if is_regression else "STABLE"
    }


if __name__ == "__main__":
    
    # Cần sửa path đúng rồi mới chạy 
    # BASE_DAT = "Để f"
    # NEW_DAT = "path/to/buggy/kieker-2023...dat"
    
    # SIG = "tools.descartes.teastore.auth.security.ShaSecurityProvider.validate"

    print("--- PPDX Local Analysis Pipeline ---")
    result = process_ppdx(BASE_DAT, NEW_DAT, SIG)
    print(result)