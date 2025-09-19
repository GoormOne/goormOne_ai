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
├── msa-ai-service/                     # FastAPI 기반 AI 서비스 (Redis/MongoDB와 연동, gRPC Client 역할)
│   ├── app/
│   │   ├── core/                       # 핵심 설정 관리
│   │   │   ├── config.py               # 환경변수, 설정값 로드
│   │   ├── db/                         # MongoDB 관련 코드
│   │   │   ├── local_init_dummy.js     # 로컬 개발용 초기 데이터 스크립트
│   │   │   ├── mongodb.py              # MongoDB 연결 및 헬퍼 함수
│   │   ├── models/                     # 데이터 모델 정의 (Pydantic/도메인 모델)
│   │   │   ├── __init__.py
│   │   │   ├── qa.py                   # QA 관련 모델 (질문/답변 구조)
│   │   │   ├── review.py               # 리뷰 데이터 모델
│   │   ├── routes/                     # API 라우터 (엔드포인트 정의)
│   │   │   ├── health.py               # 헬스체크 라우터
│   │   │   ├── qa_router.py            # QA 관련 API 라우터
│   │   │   ├── seed_router.py          # 개발용 더미 데이터 삽입 API
│   │   ├── services/                   # 서비스 로직 계층
│   │   │   ├── embedding_service.py    # gRPC 통해 임베딩 요청/저장
│   │   │   ├── rag_service.py          # RAG 실행 (검색 + 응답 생성)
│   │   │   ├── redis_service.py        # Redis Consumer/Producer (Stream 처리)
│   │   │   ├── review_watcher.py       # MongoDB Change Stream Watcher
│   │   ├── utils/                      # 유틸리티 모듈
│   │   │   ├── helpers.py              # 공통 유틸 함수
│   │   ├── __init__.py
│   │   ├── model_pb2.py                # gRPC 자동 생성 코드 (proto 기반)
│   │   ├── model_pb2_grpc.py           # gRPC 자동 생성 코드 (proto 기반)
│   │   ├── main.py                     # FastAPI 엔트리포인트
│   │   ├── test_mongo.py               # MongoDB 연결/테스트 스크립트
│   ├── Dockerfile                      # msa-ai-service용 Dockerfile
│   ├── log_config.yaml                 # 로깅 설정 파일
│   ├── requirements.txt                # Python 의존성 정의
│   └── task-definition.json            # AWS ECS 배포 정의 (Task Definition)
│
├── model-service/                      # gRPC 기반 모델 서빙 서비스 (AI 임베딩/라벨링 처리)
│   ├── app/
│   │   ├── core/                       # 공통 설정 관리
│   │   ├── db/                         # MongoDB 관련 코드
│   │   │   ├── __init__.py
│   │   │   ├── mongodb.py              # MongoDB 연결 및 헬퍼 함수
│   │   ├── ml/                         # 머신러닝/임베딩 관련 모듈
│   │   │   ├── embedding_model.py      # SentenceTransformers 모델 로딩 및 추론
│   │   ├── services/                   # 서비스 로직 계층
│   │   │   ├── labeling_service.py     # 라벨링 로직 (긍정/부정 분류 등)
│   │   ├── __init__.py
│   │   ├── main.py                     # gRPC 서버 엔트리포인트
│   │   ├── model_pb2.py                # gRPC 자동 생성 코드 (proto 기반)
│   │   ├── model_pb2_grpc.py           # gRPC 자동 생성 코드 (proto 기반)
│   ├── Dockerfile                      # model-service용 Dockerfile
│   └── requirements.txt                # Python 의존성 정의
│
├── proto/                              # gRPC 프로토콜 정의 디렉토리
│   └── model.proto                     # gRPC 서비스 및 메시지 정의
│
├── README.md                           # 프로젝트 개요/문서
└── docker-compose.yml                  # 로컬 개발 환경 (Redis, MongoDB, AI 서비스, Model Service)
```
