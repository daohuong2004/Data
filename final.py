import pandas as pd
import numpy as np
from scipy.stats import ranksums

def calculate_cliffs_delta(lst1, lst2):
    """Tính toán chỉ số Cliff's Delta (Mức độ ảnh hưởng phi tham số)"""
    m, n = len(lst1), len(lst2)
    count = 0
    for i in lst1:
        for j in lst2:
            if i > j: count += 1
            elif i < j: count -= 1
    return count / (m * n)

def signal_conditioning(data):
    """Stage 2: Loại bỏ 10 mẫu đầu (Warm-up) và lọc ngoại lệ IQR"""
    # 1. Discard Warm-up
    df_steady = data.iloc[10:].copy()
    
    # 2. IQR Filtering
    Q1 = df_steady['duration'].quantile(0.25)
    Q3 = df_steady['duration'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    
    return df_steady[(df_steady['duration'] >= lower) & (df_steady['duration'] <= upper)]

def identify_deviations(base_file, new_file):
    """Stage 3: Kiểm định thống kê hai lớp (Wilcoxon + Cliff's Delta)"""
    # Đọc dữ liệu (Kieker .dat format: tách bằng dấu ;)
    cols = ['type', 'timestamp', 'signature', 'session', 'trace_id', 'tin', 'tout', 'host', 'index', 'depth']
    df_base = pd.read_csv(base_file, sep=';', names=cols, header=None)
    df_new = pd.read_csv(new_file, sep=';', names=cols, header=None)
    
    # Tính duration (nanosecond -> millisecond)
    df_base['duration'] = (df_base['tout'] - df_base['tin']) / 1_000_000
    df_new['duration'] = (df_new['tout'] - df_new['tin']) / 1_000_000
    
    # Làm sạch dữ liệu
    S_base = signal_conditioning(df_base)
    S_new = signal_conditioning(df_new)
    
    # Kiểm định Wilcoxon (Existence)
    stat, p_val = ranksums(S_base['duration'], S_new['duration'])
    
    # Tính Cliff's Delta (Magnitude)
    d = calculate_cliffs_delta(S_new['duration'].values, S_base['duration'].values)
    
    # Cổng quyết định PPDX
    is_regression = p_val < 0.05 and abs(d) >= 0.147
    mpd_local = S_new['duration'].mean() - S_base['duration'].mean()
    
    return {
        "p_value": p_val,
        "cliffs_delta": d,
        "is_significant": is_regression,
        "mpd_ms": mpd_local
    }

# Chạy thử nghiệm cho một kịch bản
if __name__ == "__main__":
    res = identify_deviations('data/base/kieker.dat', 'data/new/kieker.dat')
    print(f"Kết quả phân tích cục bộ: {res}")