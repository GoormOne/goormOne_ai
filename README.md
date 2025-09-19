# 🍀 MSA 기반 AI 서비스 아키텍처 프로젝트

## 📌 Goal
본 프로젝트는 **MSA(Microservices Architecture)** 기반으로 **AI 서비스와 비즈니스 서비스 간의 연동**을 구현하여, 확장성과 안정성을 강화하는 것을 목표로 합니다.  
주요 목표는 다음과 같습니다:
1. **이벤트 기반 아키텍처** → Redis Stream을 활용한 비동기 메시징으로 서비스 간 느슨한 결합  
2. **AI 모델 서빙** → gRPC 기반 Python AI 서비스와 Spring 서비스 연계  
3. **실시간 데이터 처리** → MongoDB Change Stream 기반 리뷰 적재 및 임베딩 자동화  
4. **Kubernetes 오케스트레이션** → 자동 확장, 무중단 배포, 고가용성 확보  

---

## 🚨 Problem
과거에는 단일 서비스 구조로 인해 **확장성과 장애 대응**에 한계가 있었습니다.  

- 서비스 간 **직접 REST API 호출** → 독립적 확장 어려움, 장애 전파 위험  
- **동기 처리 구조** → 요청 급증 시 응답 지연 및 리소스 낭비  
- **AI 모델 호출** → 대량 요청 처리 시 성능 병목 발생  
- **분산 환경** → 데이터 흐름 추적 및 오류 분석이 어려움  

---

## 🏗️ Architecture
- **Redis Stream**: Spring → AI 서비스 간 이벤트 브로커 역할  
- **MongoDB Change Stream**: 리뷰 저장 시 자동 임베딩 생성 및 저장  
- **gRPC 통신**: FastAPI 기반 AI 서비스 ↔ Model Service (Python) 간 고성능 RPC  
- **Kubernetes**: 서비스 오케스트레이션 및 자동 확장  
- **CI/CD 파이프라인**: GitHub Actions (CI) + ArgoCD (CD), Canary 배포 적용  

---

## ⚙️ Tech Stack
- **Backend**: Spring Boot (Java), Redis, MongoDB  
- **AI Service**: FastAPI (Python), gRPC, SentenceTransformers  
- **Infra**: AWS EKS, ECR, Atlas MongoDB, Redis, Kubernetes, Helm  
- **CI/CD**: GitHub Actions, ArgoCD  
- **Monitoring**: Prometheus, Grafana, Loki  

---

## ✅ Key Features
- **비동기 메시징**: Redis Stream을 통한 Spring ↔ AI 서비스 간 통신  
- **자동 임베딩 파이프라인**: MongoDB Change Stream → gRPC Model Service 호출  
- **RAG 기반 응답 생성**: 리뷰 데이터를 활용한 검색 + 생성형 AI 응답  
- **자동 확장 & 무중단 배포** (Kubernetes HPA + Canary Deployment)  
- **관측 가능성 확보** (로그·메트릭·트레이싱 통합)  

---


```
goormOne_msa/
├── msa-ai-service/            # FastAPI 기반 AI 서비스
│   ├── app/
│   │   ├── core/              # 환경설정
│   │   │   ├── config.py      # 환경설정
│   │   ├── db/                # MongoDB 연결
│   │   │   ├── local_init_dummy.js
│   │   │   ├── mongodb.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── qa.py
│   │   │   ├── review.py
│   │   ├── routes/            # API 라우터
│   │   │   ├── health.py
│   │   │   ├── qa_router.py
│   │   │   ├── seed_router.py
│   │   ├── services/          # Redis Consumer, RAG, Embedding 서비스
│   │   │   ├── embedding_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── redis_service.py
│   │   │   ├── review_watcher.py
│   │   ├── utils/          # Redis Consumer, RAG, Embedding 서비스
│   │   │   ├── helpers.py
│   │   └── __init__.py            # FastAPI 엔트리포인트
│   │   └── model_pb2.py            # FastAPI 엔트리포인트
│   │   └── model_pb2_grpc.py            # FastAPI 엔트리포인트
│   │   └── main.py            # FastAPI 엔트리포인트
│   │   └── test_mongo.py            # FastAPI 엔트리포인트
│   ├── Dockerfile
│   ├── log_config.yaml
│   └── requirements.txt
│   └── task-definition.json
│
├── model-service/             # gRPC 기반 모델 서빙 서비스
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── mongodb.py
│   │   ├── ml/
│   │   │   ├── embedding_model.py
│   │   ├── services/
│   │   │   ├── labeling_service.py
│   │   └── __init__.py
│   │   └── main.py
│   │   └── model_pb2.py            # FastAPI 엔트리포인트
│   │   └── model_pb2_grpc.py            # FastAPI 엔트리포인트
│   ├── Dockerfile
│   └── requirements.txt
│
├── proto/                     # gRPC 프로토콜 정의
│   └── model.proto
├── README.md
└── docker-compose.yml         # 로컬 개발 환경 (Redis, MongoDB, AI 서비스, Model Service)

```
