FROM python:3.10-slim

WORKDIR /app

# تثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ المشروع
COPY . .

# المنفذ
EXPOSE 8501

# تشغيل Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
