FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium

COPY . .

EXPOSE 8501

# Shell form so ${PORT} (injected by Railway) expands at runtime.
CMD ["sh", "-c", "streamlit run ui/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false"]
