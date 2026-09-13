# 🌍 Global GHG Emissions Dashboard

## 1. Tổng quan về Data
- **Nguồn dữ liệu:** Bộ dữ liệu phát thải khí nhà kính toàn cầu (`owid-co2-data.csv`).
- **Sản phẩm thể hiện:** Dashboard trực quan hóa mức độ phát thải các loại khí (Tổng CO2, Khí Metan, CO2 từ Than đá, Xi măng...) từ năm 1990 đến 2024. Đồng thời cung cấp công cụ "Mô phỏng Kịch bản (What-if)" để dự báo ảnh hưởng của Dân số và GDP tới môi trường.
- **Vấn đề dữ liệu & Cách xử lý:**
    - *Dữ liệu thiếu (Missing Values):* Nhiều quốc gia không được ghi nhận số liệu ở một số năm. Đã xử lý bằng Pandas `fillna(0)` để tránh lỗi null khi vẽ biểu đồ.
    - *Sai lệch định dạng:* Một số cột dạng chuỗi (string) đã được ép kiểu về dạng số (numeric) thông qua `pd.to_numeric()`.
    - *Lẫn lộn dữ liệu Tổng hợp:* Dữ liệu gốc trộn lẫn số liệu của Quốc gia với số liệu của Châu lục/Toàn thế giới. Đã viết logic lọc dựa vào cột `iso_code` (quốc gia thực sự mới có mã ISO).

## 2. Kiến trúc Sản phẩm
Sản phẩm được xây dựng theo mô hình **3-Tier Architecture (FE - BE - DB)**.

### Sơ đồ Hệ thống
```mermaid
flowchart LR
    subgraph FE [Frontend - Giao diện]
        UI[Web Dashboard\n(HTML, JS, Tailwind)]
        Charts[Biểu đồ\n(Chart.js, Plotly)]
    end

    subgraph BE [Backend - Xử lý logic]
        Server[Flask Server\n(api.py)]
    end

    subgraph DB [Database - Lưu trữ]
        CSV[(Nguồn dữ liệu\nowid-co2-data.csv)]
        Pandas[(In-memory DB\nPandas)]
    end

    CSV -->|Nạp & Làm sạch| Pandas
    Pandas <-->|Truy vấn| Server
    UI -- "Gửi HTTP GET" --> Server
    Server -- "Trả về JSON" --> Charts
    Charts -.-> UI
```

### Chi tiết các cấu phần
- **Web Client (FE):** Viết bằng ngôn ngữ **HTML, JavaScript**, và sử dụng framework CSS Tailwind.
- **Server Backend (BE):** Viết bằng **Python** sử dụng framework **Flask**. 
- **Các API đã thực thi (RESTful - HTTP GET):**
    1. `/api/countries`: Lấy danh sách tên quốc gia và khoảng thời gian khả dụng để render Menu chọn lọc (Dropdown/Checkbox).
    2. `/api/stats`: Nhận tham số truy vấn (`countries`, `from`, `to`) và trả về các chỉ số KPI tổng quan (Tổng phát thải, Quốc gia cao nhất).
    3. `/api/chart/...` (map, line, bar, pie): Các endpoint chuyên biệt dùng Pandas nhóm và gom dữ liệu, trả về JSON chuẩn cho Chart.js và Plotly vẽ biểu đồ.
    4. `/api/simulation_data`: Trả về dữ liệu đa chiều (GDP, Dân số, Nhiệt độ) để Web Client tính toán kịch bản mô phỏng tương lai.

## 3. Cấu trúc Code
- `api.py`: File chứa toàn bộ logic Backend (Server), thiết lập các API endpoints và xử lý dữ liệu (Data Pipeline).
- `templates/index.html`: File Web Client (Frontend), chứa UI và các đoạn mã Javascript gửi HTTP request (fetch) tới Backend.

## 4. Thư viện & Requirements
Các thư viện Python và version được cài đặt sử dụng trong dự án:
- `Flask==3.0.3` (Dựng Web Server)
- `pandas==2.2.1` (Xử lý và làm sạch dữ liệu)
- `flask-cors==4.0.0` (Xử lý chính sách bảo mật chia sẻ tài nguyên)

## 5. Hướng dẫn Chạy Sản phẩm & Sử dụng

### Hướng dẫn bật Server
1. Mở Terminal / Command Prompt tại thư mục dự án.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install Flask pandas flask-cors
   ```
3. Chạy file server Python:
   ```bash
   python api.py
   ```
4. Mở trình duyệt web và truy cập địa chỉ: `http://127.0.0.1:5000`

### Hướng dẫn thao tác (Lọc dữ liệu)
- Ở cột bên trái, bạn có thể chọn **Nguồn phát thải** (VD: CO2 từ Dầu mỏ) và chọn **Khoảng thời gian**.
- Tick chọn vào các quốc gia trong danh sách để so sánh. Web client sẽ tự động gửi request về server và cập nhật biểu đồ không cần tải lại trang.

### Hướng dẫn Push Code lên Git
Mở terminal và gõ lần lượt các lệnh sau:
```bash
git init
git add .
git commit -m "Hoàn thiện Global GHG Dashboard"
git branch -M main
git remote add origin <link_github_repo_cua_ban>
git push -u origin main
```
