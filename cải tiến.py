import pandas as pd

def classify_severity(d):
    """Phân loại mức độ nghiêm trọng dựa trên Cliff's Delta"""
    d_abs = abs(d)
    if d_abs < 0.147: return "Negligible"
    if d_abs < 0.33:  return "Low"
    if d_abs < 0.474: return "Medium"
    return "High"

def generate_regression_report(predicted_mpd, observed_mpd, d_local):
    """Stage 5: Tạo báo cáo hồi quy và tính toán sai số"""
    
    # Tính sai số dự báo giữa mô hình kiến trúc và thực tế
    prediction_error = abs(observed_mpd - predicted_mpd)
    
    severity = classify_severity(d_local)
    
    report = {
        "Predicted_MPD_ms": predicted_mpd,
        "Actual_MPD_ms": observed_mpd,
        "Error_ms": prediction_error,
        "Severity_Level": severity,
        "Status": "REGRESSION" if predicted_mpd > 0 and d_local >= 0.147 else "STABLE"
    }
    
    return report

# Giả sử số liệu từ kịch bản L1 - N+1 Query
if __name__ == "__main__":
    # predicted_mpd: lấy từ kết quả mô phỏng QPME
    # observed_mpd: lấy từ file Script/jmeter_results.csv
    # d_local: lấy từ file final.py
    
    final_res = generate_regression_report(predicted_mpd=815.30, observed_mpd=810.50, d_local=0.85)
    
    print("--- BÁO CÁO HỒI QUY HIỆU NĂNG HỆ THỐNG (PPDX) ---")
    for key, val in final_res.items():
        print(f"{key}: {val}")