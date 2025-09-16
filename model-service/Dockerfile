# 베이스 이미지
FROM python:3.10-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 작업 디렉토리
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY app ./app

# gRPC 서버 실행
CMD ["python", "-m", "app.main"]
