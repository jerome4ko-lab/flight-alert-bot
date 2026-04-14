FROM python:3.11-slim

# 시스템 패키지
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN playwright install chromium
RUN playwright install-deps chromium

# 소스 복사
COPY . .

# data 디렉토리 생성
RUN mkdir -p data

CMD ["python", "bot.py"]
