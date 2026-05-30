import os
import sys


BASE_PATH = "/home/huong/KLTN/TeaStore"

# Định nghĩa ma trận 3 vị trí (L1, L2, L3)
LOCATIONS = {
    "L1": {
        "service": "AuthService",
        "file": f"{BASE_PATH}/tools/auth/src/main/java/tools/descartes/teastore/auth/rest/AuthUserEndpoint.java",
        "method": "public String verifyToken",
        "baseline_rt_ms": 5.0  # Thời gian thực thi chuẩn (ms)
    },
    "L2": {
        "service": "PersistenceService",
        "file": f"{BASE_PATH}/tools/persistence/src/main/java/tools/descartes/teastore/persistence/rest/ProductEndpoint.java",
        "method": "public Response getProducts",
        "baseline_rt_ms": 15.0
    },
    "L3": {
        "service": "ImageService",
        "file": f"{BASE_PATH}/tools/image/src/main/java/tools/descartes/teastore/image/rest/ImageEndpoint.java",
        "method": "public Response getImage",
        "baseline_rt_ms": 10.0
    }
}

# Định nghĩa 3 mức cường độ (Low, Medium, High)
INTENSITIES = {
    "LOW": 10,     # +10%
    "MEDIUM": 50,  # +50%
    "HIGH": 250    # +250%
}

class PPDXUltimateInjector:
    def __init__(self, loc_id, fault_type, intensity_key):
        self.loc_id = loc_id
        self.fault_type = fault_type
        self.intensity_key = intensity_key
        
        self.target = LOCATIONS[loc_id]
        # Tính toán độ trễ cần tiêm (ms)
        self.delay_ms = self.target["baseline_rt_ms"] * (INTENSITIES[intensity_key] / 100.0)
        
        self.tag_start = "// PPDX_FAULT_START"
        self.tag_end = "// PPDX_FAULT_END"

    def _get_java_code(self):
        """Tạo mã Java tương ứng với từng loại lỗi"""
        if self.fault_type == "CPU":
            delay_ns = int(self.delay_ms * 1_000_000)
            return f"""
        {self.tag_start}
        long ppdx_end = System.nanoTime() + {delay_ns}L;
        while (System.nanoTime() < ppdx_end) {{ /* Simulating CPU Intensive Regression */ }}
        {self.tag_end}"""

        elif self.fault_type == "LOCK":
            return f"""
        {self.tag_start}
        synchronized(this) {{
            try {{ Thread.sleep({int(self.delay_ms)}); }} 
            catch (InterruptedException e) {{ e.printStackTrace(); }}
        }}
        {self.tag_end}"""

        elif self.fault_type == "QUERY":
            # Giả lập lặp lại truy vấn DB (mỗi vòng lặp ~1ms)
            iterations = max(1, int(self.delay_ms))
            return f"""
        {self.tag_start}
        for(int i=0; i<{iterations}; i++) {{
            java.sql.DriverManager.getDrivers(); // Redundant DB Metadata Access
        }}
        {self.tag_end}"""
        return ""

    def run_injection(self):
        # 1. Khôi phục file về trạng thái sạch trước khi tiêm
        self.restore_all()
        
        # 2. Đọc nội dung file
        with open(self.target["file"], "r") as f:
            lines = f.readlines()

        # 3. Tìm vị trí hàm và chèn mã
        new_lines = []
        found_method = False
        injected = False
        
        for line in lines:
            new_lines.append(line)
            if self.target["method"] in line:
                found_method = True
            if found_method and "{" in line and not injected:
                new_lines.append(self._get_java_code() + "\n")
                injected = True
                found_method = False

        # 4. Ghi lại file
        with open(self.target["file"], "w") as f:
            f.writelines(new_lines)
        
        print(f"==> [SUCCESS] Injected {self.fault_type} ({self.intensity_key}) into {self.target['service']}")
        print(f"    Location: {self.target['method']}")
        print(f"    Calculated Delay: {self.delay_ms} ms")

    @staticmethod
    def restore_all():
        """Xóa sạch mọi lỗi đã tiêm trong toàn bộ hệ thống"""
        tag_start = "// PPDX_FAULT_START"
        tag_end = "// PPDX_FAULT_END"
        
        for loc in LOCATIONS.values():
            if not os.path.exists(loc["file"]): continue
            
            with open(loc["file"], "r") as f:
                lines = f.readlines()
            
            new_lines = []
            is_skipping = False
            for line in lines:
                if tag_start in line: is_skipping = True
                if not is_skipping: new_lines.append(line)
                if tag_end in line: is_skipping = False
            
            with open(loc["file"], "w") as f:
                f.writelines(new_lines)
        print("done")
# =================================================================
# GIAO DIỆN DÒNG LỆNH (CLI)
# =================================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("--- PPDX Fault Injection Driver ---")

        sys.exit(1)

    arg1 = sys.argv[1].upper()
    if arg1 == "RESTORE":
        PPDXUltimateInjector.restore_all()
    else:
        if len(sys.argv) < 4:
            print("Error: Missing parameters.")
            sys.exit(1)
        
        loc_arg = sys.argv[1].upper()   # L1, L2, L3
        type_arg = sys.argv[2].upper()  # CPU, LOCK, QUERY
        int_arg = sys.argv[3].upper()   # LOW, MEDIUM, HIGH
        
        injector = PPDXUltimateInjector(loc_arg, type_arg, int_arg)
        injector.run_injection()