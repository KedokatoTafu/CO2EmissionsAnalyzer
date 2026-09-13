# Global CO2 Dashboard Project
# 🌍 Global GHG Emissions Dashboard

Đây là project phân tích và trực quan hóa dữ liệu lượng phát thải CO2 toàn cầu, thỏa mãn các yêu cầu:
- **Dữ liệu**: CSV được làm sạch bằng Pandas.
- **API**: Flask RESTful API trả về JSON.
- **Web Client**: Xây dựng bằng HTML/Tailwind CSS, tích hợp 3 biểu đồ (Chart.js).
- **Tương tác**: Lọc theo thời gian & quốc gia; tải file CSV & biểu đồ.
- **Triển khai**: Sẵn sàng deploy thông qua Ngrok/Render.
Đây là dự án cuối khóa phân tích dữ liệu Khí nhà kính toàn cầu. Hệ thống cho phép trực quan hóa dữ liệu phát thải CO2 và các khí nhà kính từ năm 1990 - 2024, đồng thời cung cấp tính năng "Mô phỏng Kịch bản" (What-if Simulation) để dự báo biến đổi khí hậu.

## 📂 Cấu trúc thư mục
```
project1/
├── api.py                  # Server Flask xử lý API và Logic
├── co2_data_cleaned.csv    # Dữ liệu đã làm sạch
├── requirements.txt        # Các thư viện phụ thuộc
├── .gitignore              # Bỏ qua file khi dùng Git
└── templates/
    └── index.html          # Giao diện chính (Tailwind + Chart.js)
```
## 🚀 Tính năng nổi bật
- **Single Page Application (SPA):** Giao diện cực kỳ mượt mà, hỗ trợ Dark / Light Mode.
- **RESTful Flask API:** Xử lý và lọc dữ liệu bằng thư viện `pandas`.
- **Trực quan hóa đa dạng:** 5 loại biểu đồ (Plotly World Map, Line Chart, Bar Chart, Pie Chart) bằng `Chart.js` & `Plotly.js`.
- **Mô phỏng Kịch bản (What-if):** Tự động điều chỉnh các thanh trượt GDP, Dân số, Thay đổi SD đất để dự phóng mức độ phát thải trong tương lai.
- **Export Data:** Hỗ trợ tải dữ liệu lọc ra file `.csv` và xuất ảnh biểu đồ `.png`.

## 🚀 Hướng dẫn cài đặt và chạy local
## 🛠️ Cài đặt & Chạy dự án (Local)

1. **Cài đặt thư viện**:
   Mở terminal trong thư mục `project1` và chạy:
1. **Cài đặt thư viện:**
   Mở terminal và chạy lệnh sau:
   ```bash
   pip install -r requirements.txt
   pip install flask pandas flask-cors
   ```

2. **Khởi động server**:
2. **Khởi động Server:**
   ```bash
   python api.py
   ```
   *Console sẽ hiển thị: `Running on http://127.0.0.1:5000`*

3. **Truy cập Dashboard**:
   Mở trình duyệt và truy cập: [http://127.0.0.1:5000](http://127.0.0.1:5000)
3. **Truy cập:**
   Mở trình duyệt và truy cập vào: `http://127.0.0.1:5000`

## 🌐 Truy cập công khai (Dùng Ngrok)
Để share link đồ án cho người khác xem (giáo viên, bạn bè) mà không cần deploy lên server phức tạp:
1. Tải **Ngrok** tại https://ngrok.com/
2. Mở terminal mới, chạy lệnh:
   ```bash
   ngrok http 5000
   ```
3. Copy link có dạng `https://xxxx-xxx.ngrok-free.app` gửi cho giáo viên!

## 📁 Cấu trúc thư mục
- `api.py`: Backend Flask xử lý Data Pipeline và REST API.
- `templates/index.html`: Frontend UI/UX, chứa logic JavaScript.
- `owid-co2-data.csv`: Nguồn dữ liệu (Dataset gốc từ Our World in Data).
