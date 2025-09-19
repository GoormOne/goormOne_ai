# MSA 기반 서비스 아키텍처 구축 프로젝트

## ⚙️ Tech Stack
- **Backend**: Spring Boot (Java), Redis, Kafka
- **AI**: FastAPI (Python),Redis Streams, gRPC, KoSimCSE (SentenceTransformers 기반), OpenAI API (RAG 응답 생성)  
- **Infra**: AWS EKS, ECR, MSK , Kubernetes, Helm, Terraform 
- **CI/CD**: GitHub Actions, ArgoCD  
- **Monitoring**: Prometheus, Grafana, Loki  

---

## 📌 Goal
본 프로젝트는 **MSA(Microservices Architecture)** 기반으로 서비스 아키텍처를 구축하고, 확장성과 안정성을 강화하는 것을 목표로 합니다.  
주요 목표는 다음과 같습니다:
1. **이벤트 기반 아키텍처** → Redis Stream을 활용한 비동기 메시징으로 서비스 간 느슨한 결합  
2. **Kubernetes 오케스트레이션** → 자동 확장, 무중단 배포, 고가용성 확보  
3. **Observability 환경 구축** → 로그·메트릭 통합 분석, 빠른 장애 탐지·해결  
4. **AI 모델 서빙 분리** → gRPC 기반 Python Model Service와 FastAPI AI 서비스 분리  
5. **리뷰 데이터 처리 자동화** → Spring Batch 기반으로 리뷰 적재 및 사전 전처리  
6. **효율적 확장성과 비용 절감** → OpenAI API 직접 호출 대신 KoSimCSE 임베딩 모델 도입  
7. **확장성 고려 설계** → 대량 임베딩 처리 및 모델 교체 상황을 대비한 아키텍처 

---

## 🚨 Problem
과거에는 **전화 주문 중심**이었으나, 이제는 **앱 기반 실시간 주문**이 일반화되었습니다.  
하지만 기존 컨테이너 기반 MSA 환경은 프로덕션 수준에 적합하지 않았습니다.  

- 서비스 간 **직접 API 호출** → 독립적 확장 어려움, 장애 전파 위험  
- **단순 컨테이너 실행** → 배포·확장·장애 대응 자동화 한계  
- **분산 환경** → 호출 추적 및 오류 원인 분석, 성능 병목 파악 어려움  
- **동기 처리 구조** → 요청 급증 시 응답 지연 및 리소스 낭비  
- **AI 모델 호출** → 대량 요청 처리 시 성능 병목 및 OpenAI API 비용 증가  
- **애플리케이션 내부 유사도 계산** → 데이터가 늘어날수록 속도 저하, 메모리 한계 발생  


## 🏗️ Architecture

### Back-end
- **Event-driven Architecture (Kafka)**  
  주문, 결제, 재고 간 이벤트 기반 비동기 통신을 적용하여 서비스 간 결합도를 낮추고 확장성과 복원력을 강화  

- **AWS Cognito 기반 인증**  
  JWT 토큰 발급 및 그룹 기반 권한 관리로 사용자 인증·인가를 분리하고 보안성을 확보  

- **Toss Payments 연동**  
  외부 결제 API를 통해 결제 승인/취소 처리, 주문 서비스와 결제 서비스 간 상태 동기화 보장  

- **Spring Batch 기반 데이터 처리**  
  리뷰 데이터를 반정규화하여 분석/검색에 최적화된 구조로 가공, 배치 작업으로 시스템 부하 분산  

- **AI 채팅 기능 (Redis Streams)**  
  Redis Streams를 활용한 실시간 메시지 스트리밍으로 사용자 질문을 AI 서비스에 전달하고 즉각 응답 제공  

- **Saga 패턴 기반 분산 트랜잭션**  
  주문-결제-재고 흐름에서 일관성을 보장하기 위해 Orchestration 방식 Saga 적용  

- **MongoDB 연동**  
  AI 관련 문서와 리뷰 데이터를 저장 및 검색, Vector Search 기반 추천 및 RAG 응답에 활용  
 
 
### Infra

 <img width="2862" height="1542" alt="Image" src="https://github.com/user-attachments/assets/117df590-0613-482f-b142-17dcca3269e0" />


- **Kubernetes 기반 MSA 오케스트레이션**  
  EKS 클러스터 위에서 각 서비스를 독립적으로 배포 및 관리 
   
- **Helm 기반 배포 자동화**  
  Helm Chart를 활용해 Kubernetes 매니페스트를 템플릿화하고, EKS 클러스터에 일관된 방식으로 배포 자동화
  
- **CI/CD 파이프라인**  
  - **CI**: GitHub Actions 를 통해 빌드 및 테스트 자동화  
  - **CD**: ArgoCD 를 활용한 GitOps 기반 배포  
  - **Canary Deployment** 전략으로 점진적 트래픽 전환을 수행하여 안정성 확보  

- **IaC (Infrastructure as Code)**  
  Terraform 으로 VPC, EKS, RDS,MSK 등 클라우드 리소스를 선언적으로 관리하여 재현성과 일관성을 확보  


 

 ### AI
- **Redis Stream** 
	Store 서비스 → AI 서비스 간 이벤트 브로커 역할  
- **Spring Batch** 
	리뷰 데이터 적재 및 사전 처리  
- **gRPC 통신** 
	FastAPI 기반 AI 서비스 ↔ Model Service (Python) 간 고성능 RPC  
- **Model Service (Python)** 
	한국어 임베딩 특화 모델 KoSimCSE 사용, 임베딩/라벨링 추출  
- **MongoDB Atlas Vector Search** 
	Lucene 기반 HNSW 인덱스로 대규모 데이터에서도 빠른 벡터 검색  
- **FastAPI** 
	AI 서비스 엔트리포인트, Redis 구독/DB 저장/RAG 수행  
  
---
## 📈 Observability Architecture

<img width="2862" height="1542" alt="Image" src="https://github.com/user-attachments/assets/45749bd7-68cc-4b80-ae34-fddab6c7d80b" />

### 1. **App Logs Pipeline**
- **Fluent Bit (DaemonSet)**: Kubernetes 클러스터 내 모든 노드에서 실행되는 `Fluent Bit`를 사용하여 애플리케이션 로그를 수집합니다.
- **Kafka (MSK)**: `Fluent Bit`에서 수집한 로그는 `Kafka`를 통해 전송됩니다.
- **Consumer Fluent Bit**: `Kafka`에서 로그 메시지를 소비하는 `Fluent Bit` 인스턴스가 로그를 적절한 저장소로 전달합니다.
- **Loki**: 수집된 로그 데이터를 저장하는 시스템으로, `Fluent Bit`로부터 로그를 수집합니다.
- **Grafana**: `Loki`에 저장된 로그 데이터를 시각화합니다.

### 2. **Metrics Pipeline**
- **Prometheus**: 애플리케이션과 클러스터의 메트릭을 주기적으로 수집합니다.
- **Grafana**: `Prometheus`에서 수집된 메트릭 데이터를 시각화합니다.

### FLOW

1. **애플리케이션 로그 수집**  
   `Fluent Bit (DaemonSet)` → `Kafka (MSK)` → `Fluent Bit Consumer` → `Loki` → `Grafana`
   
2. **애플리케이션 메트릭 수집**  
   `Prometheus` → `Grafana`


---

## ✅ Key Features
- **자동 확장 & 무중단 배포** (Kubernetes HPA + Canary Deployment)  
- **안정적인 배포 파이프라인** (CI/CD 분리 운영)  
- **관측 가능성 확보** (로그·메트릭·트레이싱 통합)
- **이벤트 기반 아키텍처**: Kafka를 통한 주문-결제-재고 간 비동기 통신으로 서비스 간 결합도 최소화    
- **Saga 패턴 분산 트랜잭션**: 주문-결제-재고 흐름에서 데이터 일관성 보장  
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
