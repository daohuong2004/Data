

# PPDX: Early Detection of Performance Regressions in Microservices

Đây là kho lưu trữ mã nguồn và hiện vật thực nghiệm cho đề tài: **"Phát hiện sớm hồi quy hiệu năng phần mềm dựa trên dữ liệu kiểm thử cục bộ và mô hình kiến trúc"**. Phương pháp PPDX thực hiện cầu nối (bridging) giữa dữ liệu vết thực thi cấp thấp và mô hình Queueing Petri Net (QPN) để dự báo tác động hiệu năng hệ thống.

## 📂 Cấu trúc thư mục (Repository Structure)

*   `TeaStore-master/`: Mã nguồn hệ thống benchmark TeaStore.
*   `fault_injector.py`: Driver tự động "cắm" lỗi (CPU, Lock, Query) vào mã nguồn Java.
*   `kieker-2.0.3-aspectj.jar`: Tác nhân giám sát (Java Agent) để thu thập vết thực thi.
*   `teastore_model.qpe`: Mô hình kiến trúc QPN của hệ thống TeaStore (dùng cho QPME).
*   `final.py` & `cải tiến.py`: Các script Python thực hiện xử lý nhiễu (IQR), kiểm định thống kê (Wilcoxon, Cliff's Delta) và tính toán MPD.
*   `Component_perf_res/`: Dữ liệu kết quả đo lường tại cấp độ thành phần.
*   `Model_perf_res/`: Dữ liệu dự báo từ mô hình kiến trúc.
*   `qpme/`: Công cụ mô phỏng Mạng Petri hàng đợi.

## 🛠 Yêu cầu hệ thống (Prerequisites)

*   **Hệ điều hành:** Ubuntu 22.04 LTS (Khuyên dùng).
*   **Môi trường:** Docker & Docker Compose.
*   **Ngôn ngữ:** Java 8+, Maven, Python 3.8+.
*   **Thư viện Python:** `pandas`, `scipy`, `pingouin` (cho Cliff's Delta).

## 🚀 Quy trình thực nghiệm (Experimental Workflow)

Thực nghiệm bao gồm 27 kịch bản (3 vị trí x 3 loại lỗi x 3 cường độ). Thực hiện theo các bước sau:

### Bước 1: Tiêm lỗi vào mã nguồn (Fault Injection)
Sử dụng script để "cắm" lỗi vào vị trí mong muốn (L1, L2, hoặc L3).
```bash
# Ví dụ: Tiêm lỗi CPU cường độ Cao vào vị trí L1
python3 fault_injector.py L1 CPU HIGH
```

### Bước 2: Khởi động hệ thống và Thu thập vết (Tracing)
Sử dụng Docker Compose để khởi động TeaStore cùng với Kieker Agent.
```bash
sudo docker-compose up -d
# Thực hiện chạy Unit Test 40 lần để Kieker ghi lại dữ liệu vết (.dat)
for i in {1..40}; do mvn test -Dtest=AuthServiceTest; done
```

### Bước 3: Làm sạch và Phân tích thống kê (Preprocessing)
Chạy script để loại bỏ 10 run warm-up, lọc ngoại lệ IQR và thực hiện kiểm định Wilcoxon/Cliff's Delta.
```bash
python3 final.py --input ./kieker-logs --output ./S_new.csv
```
*Giai đoạn này sẽ xác định các sai lệch hiệu năng cục bộ ($\Delta rt_{local}$).*

### Bước 4: Cầu nối kiến trúc và Mô phỏng (Bridging & Simulation)
Cập nhật tham số Service Demand vào tệp `teastore_model.qpe` và chạy mô phỏng bằng công cụ QPME.
1. Mở `teastore_model.qpe` trong QPME.
2. Cập nhật giá trị $D_{new} = D_{old} + \Delta rt_{local}$.
3. Chạy **Discrete-event Simulation**.

### Bước 5: Xuất báo cáo hồi quy (Final Report)
Script sẽ tổng hợp kết quả mô phỏng và thực tế (JMeter) để tính toán sai số và mức độ nghiêm trọng.
```bash
# So sánh dự báo và thực tế
python3 cải tiến.py --model_res ./Model_perf_res --jmeter_res ./Script/jmeter_results.csv
```

## 📊 Kết quả (Results)

Phương pháp đạt được:
*   **Accuracy:** 88.9%
*   **Precision:** 87.5%
*   **Phản hồi:** 5-6 phút (Nhanh gấp ~10 lần so với kiểm thử tải truyền thống).

## 📝 Liên hệ (Contact)
*   **Tác giả:** Đào Thị Thu Hương
*   **Trường:** Đại học Công nghệ - ĐHQGHN (VNU-UET)

---
*Ghi chú: Toàn bộ dữ liệu thô và hình ảnh minh họa được đóng gói trong các tệp `data.zip.zip` và `img.zip`.*
