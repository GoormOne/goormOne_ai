FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 1. log_config.yaml 파일을 컨테이너 안으로 복사하는 라인 추가
COPY log_config.yaml .

COPY . .

# 2. CMD 명령어에 --log-config 옵션 추가
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log_config.yaml"]