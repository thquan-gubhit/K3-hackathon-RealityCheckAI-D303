<<<<<<< HEAD
# Hướng Dẫn Cài Đặt & Chạy Local (Adaptive Learning System)

Tài liệu này hướng dẫn cách setup và chạy dự án trên một máy tính mới hoàn toàn.

## Yêu cầu hệ thống
- Python 3.10 hoặc 3.11 trở lên.
- Git (để clone mã nguồn).

## Bước 1: Clone dự án và chuẩn bị môi trường
Trên máy tính mới, mở Terminal và làm theo các bước sau:

```bash
# 1. Clone repository
git clone <URL_CỦA_REPO_NÀY>
cd Batch03-K3-AI-Product-Hackathon/adaptive-learning-system

# 2. Xóa thư mục .venv cũ (nếu nó bị dính trên Git từ máy khác)
# Trên Windows:
rmdir /s /q .venv
# Trên Mac/Linux:
rm -rf .venv

# 3. Tạo môi trường ảo (virtual environment) mới cho máy tính này
python -m venv .venv

# 4. Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Trên Mac/Linux:
source .venv/bin/activate
```

## Bước 2: Cài đặt thư viện
Nếu dự án chưa có file `requirements.txt`, bạn cần cài đặt thủ công các thư viện cốt lõi bằng lệnh sau:

```bash
pip install fastapi uvicorn pydantic streamlit sqlalchemy openai python-dotenv
```
*(Nếu hệ thống báo thiếu thư viện nào khác lúc chạy, hãy dùng `pip install <tên_thư_viện>` để bổ sung và sau đó chạy `pip freeze > requirements.txt` để lưu lại cho máy khác nhé).*

## Bước 3: Cấu hình biến môi trường
Dự án cần một file `.env` chứa cấu hình (như API key). 
1. Tạo một file tên là `.env` trong thư mục `adaptive-learning-system`.
2. Mở file và điền các biến cần thiết (tham khảo code hoặc team member), ví dụ:
```env
OPENAI_API_KEY=sk-your-openai-api-key
ENVIRONMENT=development
```

## Bước 4: Khởi chạy Backend (FastAPI)
Mở một cửa sổ Terminal (đảm bảo đã kích hoạt `.venv`), chạy lệnh:

```bash
cd adaptive-learning-system
uvicorn app.main:app --reload --port 8000
```
- Backend sẽ chạy tại: `http://localhost:8000`
- Tài liệu API (Swagger UI): `http://localhost:8000/docs`

## Bước 5: Khởi chạy Frontend (Streamlit)
Mở thêm **một cửa sổ Terminal thứ hai** (vẫn phải kích hoạt `.venv`), chạy lệnh:

```bash
cd adaptive-learning-system
streamlit run frontend/Home.py
```
- Giao diện web sẽ tự động bật lên trên trình duyệt tại: `http://localhost:8501`

---
> **Lưu ý quan trọng cho Team:** 
> Thư mục `.venv` là thư mục chứa thư viện biên dịch riêng cho từng máy, **tuyệt đối không được push lên Git**. Đảm bảo rằng file `.gitignore` ở cấp cao nhất đã có dòng `.venv/`.
=======
# 🚀 Hướng Dẫn Thiết Lập & Khởi Chạy Reality Check AI (Local Setup)

Tài liệu này hướng dẫn chi tiết cách cài đặt, cấu hình và khởi chạy trọn bộ hệ thống **Reality Check AI** (bao gồm Trí tuệ AI Backend và Giao diện React/Vite Hiện đại) trên một máy tính cá nhân hoặc môi trường kiểm thử mới.

---

## 🛠️ 1. Yêu Cầu Kỹ Thuật (Prerequisites)

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã được trang bị các phần mềm cốt lõi:
- **Python 3.10 hoặc 3.11+** (Dùng cho tầng Backend Xử lý AI, đọc phân tích Slide PDF & chấm điểm Active Recall).
- **Node.js 18+ và Npm** (Dùng để đóng gói và hiển thị Giao diện Người dùng sang trọng React/Vite).
- **Git** (Để tải mã nguồn từ kho lưu trữ).

---

## 📥 2. Cài Đặt Môi Trường (Setup Workspace)

### Bước 2.1: Tải mã nguồn & Vào thư mục hệ thống
Mở Terminal (Command Prompt / Windows PowerShell / Terminal MacOS) và thực thi:

```powershell
# 1. Clone kho lưu trữ
git clone <URL_KHO_LUU_TRU_CUA_DUI_AN>
cd Batch03-K3-AI-Product-Hackathon/adaptive-learning-system
```

---

### Bước 2.2: Thiết lập tầng Trí Tuệ AI (Backend Environment)
Ngay bên trong thư mục `adaptive-learning-system/`:

```powershell
# 1. Tạo môi trường ảo riêng biệt cho dự án (để không đụng độ với các app khác trên máy)
python -m venv .venv

# 2. Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Trên Mac / Linux:
source .venv/bin/activate

# 3. Cài đặt trọn bộ thư viện lõi cho Backend (FastAPI, Uvicorn, OpenAI, PyMuPDF, SQLAlchemy...)
pip install --upgrade pip
pip install -r requirements.txt
```

> [!IMPORTANT]
> Thư viện **PyMuPDF (`fitz`)** đã được khai báo sẵn trong `requirements.txt`. Đây là bộ máy lõi chịu trách nhiệm bóc tách và tạo hình ảnh Slide PDF sắc nét giúp hiển thị trực diện trên giao diện web trong thời gian thực.

---

### Bước 2.3: Cấu hình Khóa trí tuệ AI (Environment Variables)
Hệ thống sử dụng mô hình trí tuệ nhân tạo tiên tiến để chia nhỏ slide và thấu hiểu ngữ cảnh làm bài thi của người dùng:
1. Tạo một tệp tin mới mang tên chính xác là **`.env`** ngay trong thư mục gốc `adaptive-learning-system/`.
2. Mở file `.env` bằng bất kỳ phần mềm soạn thảo văn bản nào (VSCode, Notepad) và cấu hình như sau:

```ini
# Khóa kết nối API (Bắt buộc phải có để AI phân tích Slide và chấm câu hỏi)
OPENAI_API_KEY="sk-your-real-openai-api-key-here"

# Thiết lập mô hình LLM (Khuyên dùng gpt-4o để có hiệu suất chuẩn đoán ngộ nhận cao nhất)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o

# Cấp độ thông báoật nhật ký hoạt động (INFO: Hiện tiến trình 깔끔, DEBUG: Hiện toàn bộ chi tiết)
LOG_LEVEL=INFO

# Cấu hình dữ liệu
APP_ENV=development
```

---

### Bước 2.4: Khởi tạo Cơ sở Dữ liệu (Database Prep)
Để tạo sẵn bảng theo dõi điểm số, lộ trình bài học và lịch sử Active Recall:
```powershell
python scripts/init_db.py
```
*(Lệnh này sẽ tạo ra tệp tin csdl nhúng `data/app.db` vô cùng siêu nhấp, sẵn sàng tiếp thu bài học mới).*

---

### Bước 2.5: Cài đặt Giao diện Người Dùng (React Frontend Prep)
Di chuyển vào thư mục giao diện và tải các mô-đun hỗ trợ hiệu ứng hiển thị:

```powershell
# 1. Đi vào thư mục giao diện React
cd react-frontend

# 2. Cài đặt gói node_modules
npm install
```

---

## ⚡ 3. Hướng Dẫn Khởi Chạy Hệ Thống & Kiểm Thử (How to Run)

Để hệ thống hoạt động hoàn hảo (Bộ não AI nhận dữ liệu từ Giao diện UI/UX), bạn cần chạy đồng thời **2 máy chủ song song trên 2 tab Terminal**.

### 🖥️ Terminal 1: Khởi động Trái tim Trí tuệ AI (Backend API Server)
Từ thư mục `adaptive-learning-system/` (sau khi đã kích hoạt `.venv`):

```powershell
# Cách A (Sử dụng kịch bản tiện lợi của hệ thống):
python scripts/run_backend.py

# Cách B (Hoặc chạy trực tiếp qua máy chủ Uvicorn):
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- 🟢 **Bản kiểm nghiệm API:** Cổng dữ liệu ngầm phát sóng tại `http://127.0.0.1:8000`.
- 📖 **Tài liệu trực quan (Swagger OpenAPI):** Bạn có thể ghé thăm `http://127.0.0.1:8000/docs` để kiểm tra các phương thức giao tiếp của hệ thống.

---

### 🌐 Terminal 2: Khởi động Trình diễn Giao diện (Modern React UI)
Mở một cửa sổ Terminal thứ hai, sau đó:

```powershell
# Cách A (Sử dụng lệnh kịch bản Python cải tiến — Tự động nhận diện và gọi React Vite):
python scripts/run_frontend.py

# Cách B (Hoặc khởi chạy chuẩn theo quy trình NPM trong thư mục):
cd react-frontend
npm run dev
```

---

## 🎯 4. Trải Nghiệm & Hướng Dẫn Bỏ Túi cho Hội Đồng Thẩm Định
Sau khi bật 2 máy chủ, hãy truy cập Trình duyệt Web của bạn tại địa chỉ:
👉 **`http://localhost:5173/`**

### Các điểm nhấn tính năng nổi bật (UX Walkthrough):
1. **Giao tiếp Song ngữ Anh - Việt lập tức:** Góc trên phải màn hình có thanh chuyển đổi 언어 (VN / EN). Bạn có thể thử nghiệm nghiệm thu tính năng chuyển ngữ toàn bộ kịch bản AI tức thì.
2. **Kẹo chớp sáng "Hệ thống đang hoạt động" (Live Health Indicator):** Nếu chấm tròn đổi sang màu Xanh Lá, Frontend đã thông luồng giao thoa thành công với Backend API Port 8000.
3. **Thả Slide trực quan & Xử lý lộ trình học tập:** Thả tệp ttin PDF vào Drop zone. AI sẽ bẻ khoá và vẽ ra Bản đồ Kiến thức theo nhánh chuyên đề (Knowledge Map).
4. **Học Tập Qua Slide Gốc & AI Tóm Tắt (Phase Reading):**
   - Khi chọn một mục chuyên đề, người dùng được cung cấp một Rạp chiếu mini cho xem trực diện từng Trang **Slide gốc** bản thật tương ứng với chuyên đề đó (`← Slide trước` / `Slide tiếp →`).
   - Ngay bên dưới là thẻ bài học được AI chiêm nghiệm & vạch ra các điểm: *Mục tiêu cốt lõi*, *Khái niệm trọng tâm*, và đặc biệt là *⚠️ Hiểu lầm thường gặp (Misconception Warnings)* trước giờ G!
5. **Vượt Cửa Kiểm Tra Thi Sâu (Active Recall Testing):** Bấm nút xác nhận tiếp thu để làm các bài thực nghiệm tự luận ngắn,AI sẽ tự phân tách lời bình và đánh giá độ Tường Minh (Mastery Score) cho từng chu kỳ con.

---

## ❓ 5. Giải Đáp Nhanh & Xử Lý Sự Cố (FAQ & Troubleshooting)

| Hiện tượng | Nguyên nhân & Cách Xử lý Nhanh |
| :--- | :--- |
| **Báo lỗi `HTTP 422` hoặc `500 Internal Server Error` lúc nộp bài** | Đảm bảo khóa `OPENAI_API_KEY` trong file `.env` còn số dư và chính xác. Thử ngắt và làm trống csdl nháp bằng cách xóa `data/app.db` và chạy lại `python scripts/init_db.py`. |
| **Báo lỗi `Port 8000 already in use` hoặc `Port 5173 inside use`** | Máy tính có thể đang treo 1 Terminal ngầm từ trước. Hãy đóng các tab terminal cũ hoặc tắt uvicorn node bằng lệnh quản lý trình tiết kiệm máy rồi cất cánh lại. |
| **Nhật ký Hệ thống (Logs) lưu ở đâu?** | Mặc định, nhật ký sẽ cuộn theo thời gian thực (realtime streaming) trên màn hình Terminal 1 mà **không lưu tốn đĩa**. Nếu muốn xuất ra file (để nộp báo cáo), gõ thêm đuôi lệnh: `python -m uvicorn app.main:app --port 8000 > backend.log 2>&1`. |
| **Tại sao Giai đoạn Gia sư AI (AI Tutor) báo "Tính năng đang phát triển"?** | Đây là thiết kế bảo đảm trải nghiệm cho người dùng! Giao diện Chat tự do đang được chuyển hướng minh bach, giúp AI dù chốt ngộ nhận vẫn giữ cho người dùng tiếp bước luồng báo cáo điểm thấu đáo mà không vấp đứt gánh giữa chừng! |

---

*Chúc Đội thi và Quý Hội đồng Thẩm định có chuỗi trải nghiệm đánh giá chuyên sâu tuyệt vời với **Reality Check AI**! 🏆*
>>>>>>> tuan
