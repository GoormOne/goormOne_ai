# 🍀 MSA 기반 AI 서비스 아키텍처 프로젝트

## 📌 Goal
본 프로젝트는 **MSA(Microservices Architecture)** 기반으로 **AI 서비스와 비즈니스 서비스(Spring)** 간의 연동을 구현하여, 확장성과 안정성을 강화하는 것을 목표로 합니다.  
주요 목표는 다음과 같습니다:
1. **이벤트 기반 아키텍처** → Redis Stream을 활용한 비동기 메시징으로 서비스 간 느슨한 결합  
2. **AI 모델 서빙 분리** → gRPC 기반 Python Model Service와 FastAPI AI 서비스 분리  
3. **리뷰 데이터 처리 자동화** → Spring Batch 기반으로 리뷰 적재 및 사전 전처리  
4. **효율적 확장성과 비용 절감** → OpenAI API 직접 호출 대신 KoSimCSE 임베딩 모델 도입  
5. **확장성 고려 설계** → 대량 임베딩 처리 및 모델 교체 상황을 대비한 아키텍처  

---

## 🚨 Problem
과거에는 단일 서비스 구조로 인해 **확장성과 장애 대응**에 한계가 있었습니다.  

- 서비스 간 **직접 REST API 호출** → 독립적 확장 어려움, 장애 전파 위험  
- **동기 처리 구조** → 요청 급증 시 응답 지연 및 리소스 낭비  
- **AI 모델 호출** → 대량 요청 처리 시 성능 병목 및 OpenAI API 비용 증가  
- **애플리케이션 내부 유사도 계산** → 데이터가 늘어날수록 속도 저하, 메모리 한계 발생  

---

## 🏗️ Architecture
- **Redis Stream**: Spring → AI 서비스 간 이벤트 브로커 역할  
- **Spring Batch**: 리뷰 데이터 적재 및 사전 처리  
- **gRPC 통신**: FastAPI 기반 AI 서비스 ↔ Model Service (Python) 간 고성능 RPC  
- **Model Service (Python)**: 한국어 임베딩 특화 모델 KoSimCSE 사용, 임베딩/라벨링 전담  
- **MongoDB Atlas Vector Search**: Lucene 기반 HNSW 인덱스로 대규모 데이터에서도 빠른 벡터 검색  
- **FastAPI**: AI 서비스 엔트리포인트, Redis 구독/DB 저장/RAG 수행  

---

## ⚙️ Tech Stack
- **Backend**: Spring Boot (Java), Spring Batch, Redis, MongoDB Atlas  
- **AI Service**: FastAPI (Python), gRPC, KoSimCSE (SentenceTransformers 기반), OpenAI API (일부 RAG 응답 생성)  
- **Infra**: Docker, Docker Compose, AWS (ECR/EKS), Kubernetes, Helm  
- **CI/CD**: GitHub Actions, ArgoCD  
- **Monitoring**: Prometheus, Grafana, Loki  

---

## ✅ Key Features
- **비동기 메시징**: Redis Stream으로 Spring ↔ AI 서비스 간 통신  
- **서버 분리 & gRPC**: 임베딩 전담 Model Service와 AI 서비스 분리 → 성능 최적화, 확장성 확보  
- **임베딩 비용 절감**: OpenAI API 대신 KoSimCSE 활용 → 한국어 특화 성능 + 비용 감소  
- **Vector Search 도입**: MongoDB Atlas HNSW 기반 인덱스를 활용해 대규모 리뷰 데이터에서도 빠른 검색  
- **RAG 기반 응답 생성**: 질문 임베딩 + 리뷰 임베딩 비교 후 LLM 프롬프팅을 통한 응답 생성  
- **확장성 고려**: Model Service만 따로 스케일 아웃 가능, 데이터가 늘어도 성능 유지  

---

## 📂 Project Structure
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
