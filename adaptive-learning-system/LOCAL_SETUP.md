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
