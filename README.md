# SKN14-FINAL-2Team

<<<<<<< HEAD
### ☘️ 팀명: ScentLab  
### 🌳 프로젝트명: ScentPick  
=======
### ☘️팀명: ScentLab
### 🌳홈페이지: ScentPick (https://scentpick.store)

### **🧴ScentPick: LLM 기반으로 맞춤형 향수를 추천하는 대화형 챗봇 서비스**
>>>>>>> 8d1479cf512c63c46337e233b8d1d59a1ef885c2


## 🧴 ScentPick: LLM 기반 맞춤형 향수 추천 챗봇 서비스

> ScentPick은 **대화형 RAG 기반 챗봇**으로, 사용자가 일상적인 언어(“여름 바닷가의 시원한 향”, “무겁지 않은 출근용 향”)로 입력하면  
AI가 이를 이해하고 개인 맞춤형 향수를 추천해주는 서비스입니다.  

- **기존 문제점**
  1. 수천 가지 향수 중 원하는 향을 찾기 어려움  
  2. 노트·어코드 등 전문 용어 중심 → 일반 소비자가 이해하기 어려움  
  3. 매장 접근성·높은 가격·시향 불가 문제  

<<<<<<< HEAD
- **해결 목표**  
  자연어 기반 대화형 인터페이스 + 벡터 검색 + 멀티모달 기능을 통해  
  사용자가 쉽게 본인 취향에 맞는 향수를 찾도록 지원  
=======
### 🎇 Features 🎇
- **RAG기반의 Chatbot** : 
    - RAG 기술로 향수 브랜드 전체 데이터베이스에서 필요한 부분을 가져오는 기능 
    - 로그인한 고객 대상으로 채팅 히스토리를 제공하는 기능 
    - 실시간으로 고객과 챗봇의 질의응답 대화가 가능
    - 이미지 업로드하면 분위기에 맞는 향수를 추천하는 **멀티모달** 기능  
- **사용자의 의견을 반영한 추천 시스템** :
    - 사용자가 원하는 노트와 향 종류를 반영하여 적절한 향수 제품을 추천하는 기능
      
- **간결하고 직관적인 UI** 

>>>>>>> 8d1479cf512c63c46337e233b8d1d59a1ef885c2

<img src="./images/프로젝트개요.png" alt="프로젝트 개요 이미지" />

<<<<<<< HEAD
<br>
=======
- 개발 환경: Pycharm, VSCode
- 기술 스택
<img width="826" height="353" alt="Image" src="https://github.com/user-attachments/assets/07c03098-faf3-4959-8e24-980fc9cece3f" />
>>>>>>> 8d1479cf512c63c46337e233b8d1d59a1ef885c2

## 👨‍💻 팀원 소개

<<<<<<< HEAD
| **박빛나** | **유용환** | **한성규** | **강윤구** | **전정규** | **정유진** |
|:----------:|:----------:|:----------:|:----------:|:----------:|:----------:|
| <img src="./images/박빛나_향수.jpg" width="120px" alt="박빛나 프로필 이미지"> | <img src="./images/yonghwan.png" width="120px" alt="유용환 프로필 이미지"> | <img src="./images/seonggyu.png" width="120px" alt="한성규 프로필 이미지"> | <img src="./images/yungoo.png" width="120px" alt="강윤구 프로필 이미지"> | <img src="./images/jeonggyu.png" width="120px" alt="전정규 프로필 이미지"> | <img src="./images/yujin.png" width="120px" alt="정유진 프로필 이미지"> |
| [`@ParkVitna`](https://github.com/ParkVitna) | [`@yooyonghwan111`](https://github.com/yooyonghwan111) | [`@Seonggyu-Han`](https://github.com/Seonggyu-Han) | [`@dbsrn09`](https://github.com/dbsrn09) | [`@jeonggyu`](https://github.com/jeonggyu) | [`@rainbow0291`](https://github.com/rainbow0291) |
=======


### 📝 Table of Content

- 팀원소개
- ScentPick 챗봇서비스 소개
- 주요 기능
- 시스템 아키텍처
- 데이터 구조
- 향수 웹사이트 화면
- 인공지능 모델링
- 시스템 통합
- 최종 개발
- 기대 효과 
- Contact


### 팀원 소개

| 이름   | GitHub ID      | 업무                                                                                       |
|---------|----------------|------------------------------------------------------------------------------------------|
| 박빛나  | ParkVitna      | PM(프로젝트 매니저), 프로젝트 관리, 데이터 크롤링 및 정제, 프로젝트 기획서 작성, django ORM, AWS 배포, CI/CD               | 
| 유용환  | yooyonghwan111 | RM(리소스 매니저), Pinecone Vector DB 구축, wbs 작성, 데이터 조회 프로그램 작성, 시스템 아키텍처 구조, LangGraph 챗봇 설계 | 
| 한성규  | Seonggyu-Han   | 향수 데이터 수집, 전처리 및 정제, UI 구성,  API 조사, 데이터베이스 설계문서 작성, FastAPI, 챗봇, 웹사이트 페이지 검수      |
| 강윤구  | dbsrn09        | 향수 데이터 크롤링, 정제, 챗봇 사용자 입력 전처리 , 오프라인(map) 페이지, 상세페이지 및 마이페이지 검수,수정               | 
| 전정규  | jung33010      | 머신러닝 메인 어코드 추출 기능, FastAPI, LangGraph 챗봇 설계, AWS배포, CI/CD                                              | 
| 정유진  | rainbow0291    | UI 구성, 화면 설계 및 기능 구체화, README 파일, 회의록, 요구사항 정의서 작성, 상세페이지 작성                               | 


### 🧴ScentPick 챗봇서비스 소개

- 사용자가 원하는 조건에 맞게 향수를 3가지 추천해주는 챗봇 구현
- 향수 이름, 향수 브랜드, 향수 종류, 향 설명, 가격, 용량, 메인 어코드, 탑/미들/베이스 노트 데이터를 DB에 저장
- 참고 링크
<img width="1427" height="679" alt="Image" src="https://github.com/user-attachments/assets/1e4b6971-1b67-4fb8-b028-5573b7c274de" />


### 📱 주요 기능
- **즐겨찾기** 기능: 로그인한 경우 마이페이지에 선택한 향수를 표시하는 기능
- **챗봇추천** 기능: 사용자가 작성한 조건에 맞게 3가지 향수를 추천해주는 기능
- 링크: 추천된 향수이름을 클릭하면 해당 제품 **상세페이지**로 연결되는 기능
- 로그인하고 마이페이지에서 챗봇과 **대화내역**chat history  저장, 표시되는 기능
- 향 설명, 탑/미들/베이스 노트, 용량 등의 **정보를 제공**하는 기능
- 향수노트/어코드/브랜드/이미지 등 도메인 엔터티 관리
- RAG 검색을 위한 임베딩/소스 문서 관리

* 초기 페이지 구상  
<img width="212.8" height="120.9" alt="Image" src="https://github.com/user-attachments/assets/bb77a9bd-213f-4f8c-8779-c70a985c2340" />
<img width="214.2" height="120.1" alt="Image" src="https://github.com/user-attachments/assets/dda1392d-caa3-404e-9f33-6a0b7d155d18" />
<img width="100.3" height="100.4" alt="Image" src="https://github.com/user-attachments/assets/d8a3b79b-8001-42a4-95f9-777174a41153" />
<img width="200.8" height="100.4" alt="Image" src="https://github.com/user-attachments/assets/8bcac447-f498-4817-a4f9-011cd2c4b179" />


>>>>>>> 8d1479cf512c63c46337e233b8d1d59a1ef885c2


<br>

<<<<<<< HEAD
## 🛠️ 기술 스택
=======
<img width="1911" height="651" alt="Image" src="https://github.com/user-attachments/assets/f4830031-5058-4767-ac3a-aaab4dbe9c36" />

<img width="655" height="464" alt="Image" src="https://github.com/user-attachments/assets/624ce6a7-12a7-41b7-9b44-1768c083929e" /> <br>
- LLM_parser         : 2개 이상의 다중 제품 속성(facets) 쿼리를 파싱/정규화.
- FAQ_agent          : 향수 지식/정의/차이/일반 질문.
- human_fallback     : 비(非)향수 또는 오프토픽.
- price_agent        : 가격 전용 의도(cheapest, price, buy, discount 등).
- ML_agent           : 단일 취향/무드 추천 및 최근 추천 결과에 대한 FOLLOW-UP.
- memory_echo        : 사용자가 "방금 내가 뭐라고 했지?" / 마지막 질문을 묻는 경우.
- rec_echo           : 사용자가 "네가 방금 추천한 목록/이름 다시 보여줘"를 요청하는 경우.
>>>>>>> 8d1479cf512c63c46337e233b8d1d59a1ef885c2

| 카테고리 | 기술 |
|----------|------|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) |
| **DevOps** | ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?logo=gunicorn&logoColor=white) ![AWS Elastic Beanstalk](https://img.shields.io/badge/AWS_Elastic_Beanstalk-FF9900?logo=amazonaws&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white) |
| **Frontend** | ![Django](https://img.shields.io/badge/Django_Template-092E20?logo=django&logoColor=white) ![Figma](https://img.shields.io/badge/Figma-F24E1E?logo=figma&logoColor=white) |
| **Data Collection** | ![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=white) ![WebDriver](https://img.shields.io/badge/WebDriver-grey?logo=googlechrome&logoColor=white) ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-3776AB?logo=python&logoColor=white) |
| **AI** | ![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white) ![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-000000?logo=huggingface&logoColor=white) ![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?logo=huggingface&logoColor=black) ![Embeddings](https://img.shields.io/badge/Embeddings-007ACC?logo=openai&logoColor=white) |
| **Database** | ![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white) ![Pinecone](https://img.shields.io/badge/Pinecone-005571?logo=pinecone&logoColor=white) |

<br>

## 🧴 ScentPick 챗봇서비스 소개

- 사용자가 자연어 또는 이미지로 입력하면, AI가 향을 이해하고 향수를 추천  
- RAG 구조를 통해 **DB + VectorDB + LLM** 결합  
- 추천된 향수는 상세 페이지와 마이페이지에서 관리 가능  
- 날씨·계절·성별 기반 추천, 향수 월드컵(토너먼트) 등 콜드스타트 대응 기능 포함  

<br>

## 📱 주요 기능

- **챗봇 추천 (RAG 기반)**  
  - 사용자의 자유로운 언어 입력을 구조화 → 적합한 향수 추천  
  - 실시간 스트리밍 응답(SSE) → 타이핑 효과  

- **멀티모달 추천**  
  - 이미지 업로드 시 GPT-4o-mini가 분석 → 분위기/계절/성별 기반 추천  

- **추천 페이지**  
  - 오늘의 날씨·계절과 로그인한 사용자 성별 반영  
  - 향수 월드컵(토너먼트)로 취향 탐색  

- **향수 전체 목록 페이지**  
  - 모든 향수 데이터를 보여주는 카탈로그 페이지  
  - 브랜드, 성별, 농도, 메인 어코드 등 다양한 조건으로 필터링이 가능

- **향수 상세 페이지**  
  - 개별 향수의 상세 정보(설명, 노트 구성, 용량 등) 확인  
  - 사용자별 즐겨찾기 추가/제거, 좋아요/싫어요 피드백 가능

- **오프라인 매장 안내**  
  - 카카오맵 API 기반으로 주변 향수 매장 검색 및 지도 표시  

- **마이페이지**  
  - 추천 내역 확인 (날짜, 브랜드, 횟수)  
  - 좋아요/싫어요/즐겨찾기 관리  
  - 프로필 수정 및 이미지 업로드 (S3 저장)  


<img src="images/주요기능예시화면01.png" alt="주요 기능 예시 화면 01" />
<img src="images/주요기능예시화면02.png" alt="주요 기능 예시 화면 02" />

<br>

## 🖥️ 시스템 아키텍처

<<<<<<< HEAD
- **Frontend (Django Template)**  
  로그인/회원가입, 챗봇 UI, 추천 결과, 마이페이지  

- **Backend (FastAPI)**  
  멀티에이전트 라우터 (LangGraph 기반)  
  - Supervisor → LLM_parser, ML_agent, review_agent, price_agent, multimodal_agent, FAQ_agent 등으로 라우팅  
  - Pinecone VectorDB와 OpenAI GPT-4o-mini를 결합한 RAG 응답 생성  

- **Database (AWS RDS, Pinecone, S3)**  
  - RDS: 유저·대화·추천 로그 관리  
  - S3: 이미지 저장 (프로필, 향수 이미지)  
  - Pinecone: 향수 스펙·리뷰·키워드 임베딩 벡터 검색  
=======

### 🔢데이터 구조 
<img width="1345" height="893" alt="Image" src="https://github.com/user-attachments/assets/3efa6c42-0033-4bbb-9800-28ef03d8578b" /> <br>

### 향수 웹사이트 화면 <br>
 1. 메인화면 <img width="1171" height="847" alt="Image" src="https://github.com/user-attachments/assets/60cf6ae4-772f-4ab1-bb70-942e87b78bb4" />  <br>
 2. 챗봇 페이지 <img width="1196" height="804" alt="Image" src="https://github.com/user-attachments/assets/c43855cd-676e-4bcb-988a-223dc134a9a3" />  <br>
 3. 추천 페이지(날씨에 따른 추천 등) <img width="1171" height="829" alt="Image" src="https://github.com/user-attachments/assets/9a54bb1b-060d-46c5-bdbf-592b6bce23f8" />  <br>
 4. 전체 향수 리스트 페이지(조건에 따른 필터링 가능) <img width="1205" height="850" alt="Image" src="https://github.com/user-attachments/assets/5d2f9ffa-d826-4735-9734-223a881cce5e" />  <br>
 5. 상세페이지(802개의 향수 특징- 성별/계절별/시간대별/노트별 특성) <img width="789" height="857" alt="Image" src="https://github.com/user-attachments/assets/e5e3eff1-e4dc-4da2-b1b3-97ec4e83c225" />  <br>
 6. 오프라인 페이지(향수 매장 지도)<img width="1183" height="701" alt="Image" src="https://github.com/user-attachments/assets/983bef42-3c3f-4b2e-87e4-53099d8a8e39" />  <br>
 7. 마이페이지(즐겨찾기, 선호/비선호, 추천받은 향수 목록)<img width="1175" height="814" alt="Image" src="https://github.com/user-attachments/assets/f752a9db-2a2b-4cbd-8dae-6371808621dd" />  <br>
 8. 로그인페이지 <img width="1149" height="728" alt="Image" src="https://github.com/user-attachments/assets/e446197c-44dd-4106-a4b1-20fd8e308a15" />  <br>
 9. 회원가입페이지 <img width="1089" height="857" alt="Image" src="https://github.com/user-attachments/assets/8661b604-c71e-48eb-ad96-2ddc46b21e14" />  <br>

### 인공지능 모델링
- 사용자의 자연어 향 설명에서 적절한 향수 메인 어코드를 분류
- LLM 활용 모델 개발(자연어 입력하면 핵심 속성 추출(향 설명, 가격, 브랜드, 용량 등))
- LangChain + OpenAI 연동
- 시스템 아키텍처 설계
- HuggingFace dataset 머신러닝 다중분류모델 성능 평가
- 원본데이터 <img width="839" height="412" alt="Image" src="https://github.com/user-attachments/assets/7fa357f9-6818-4165-918b-e81df411ca73" />  <br>

- 향 설명과 메인 어코드 추출 
- ① 수집 → ② 결측치 처리 → ③ 불필요 단어 제거 → ④ 브랜드/향수명 제거 → ⑤ 숫자/특수문자 제거 → ⑥ 소문자 변환 → ⑦ 학습/검증 데이터 분리
- 허깅페이스 데이터셋 최종 채택 모델: 
- XLM-Roberta base + Classification Head
 (transformers.AutoModelForSequenceClassification, problem_type="multi_label_classification")	
<img width="547" height="431" alt="Image" src="https://github.com/user-attachments/assets/dad82f8c-03ac-4d67-88ca-a694c4e5a57f" />  <br>

<img width="531" height="100" alt="Image" src="https://github.com/user-attachments/assets/44752229-69f4-45db-bba8-cafba604ba09" />  <br>
- **학습 결과 및 성능 평가**
<img width="634" height="619" alt="Image" src="https://github.com/user-attachments/assets/1e556e61-fc4c-4211-9d33-a2d36e742a92" />  <br>

<img width="617" height="466" alt="Image" src="https://github.com/user-attachments/assets/1bc5e614-d3d3-415c-b1a8-052303b90e42" />  <br>
- 주요 지표(검증 셋)
- threshold=0.5 기준 Epoch 5~7 최고점
- Micro-F1 ≈ 0.53
- Macro-F1 ≈ 0.33~0.34
- Jaccard ≈ 0.42~0.43
- 참고: 검증 Loss는 Epoch 5 이후 상승(과적합 경향), Micro-F1도 이후 정체/하락 
→ 5~7 사이 모델이 가장 타당.
결론: XLM-R 파인튜닝 + pos_weight + label threshold로 Micro-F1≈0.53 달성
>>>>>>> 8d1479cf512c63c46337e233b8d1d59a1ef885c2


## 🔗 시스템 통합

- Django와 FastAPI를 API로 연동  
- SSE 기반 스트리밍 응답 구현  
- OAuth2 소셜 로그인(Google, Kakao, Naver)  
- AWS 환경 배포 (Elastic Beanstalk, EC2, RDS, S3, Route53)  
- Docker 기반 CI/CD 파이프라인  

<img src="images/시스템아키텍쳐.png" alt="시스템 아키텍처 다이어그램" />

<br>

## 🔢 데이터 구조

- **MySQL (RDS)**  
  - perfumes: 향수 기본 정보  
  - note_images: 노트별 이미지  
  - users / user_detail: 회원 정보  
  - conversations / messages: 대화 세션 기록  
  - favorites / feedback_events: 좋아요·싫어요·즐겨찾기  
  - rec_runs / rec_candidates: 추천 실행 기록  

- **Pinecone Vector DB**  
  - perfume-vectordb: 향수 스펙 (802개)  
  - review-vectordb: 사용자 리뷰 (6,591건)  
  - keyword-vectordb: 노트-어코드 매핑 (53개)  

<img src="images/erd데이터구조.png" alt="ERD 데이터 구조" />

<<<<<<< HEAD
<br>

## 🖼️ 향수 웹사이트 화면

## 🖼️ 향수 웹사이트 화면

| 페이지 | 화면 예시 |
|--------|-----------|
| **메인 페이지** | <img src="images/main_page.png" alt="메인 페이지 화면" width="400px" /> |
| **향수 목록 페이지** | <img src="images/perfume_list.png" alt="향수 목록 페이지 화면" width="400px" /> |
| **향수 상세 페이지** | <img src="images/perfume_detail.png" alt="향수 상세 페이지 화면" width="400px" /> |
| **챗봇 추천** | <img src="images/chatbot.png" alt="챗봇 추천 UI 화면" width="400px" /> |
| **멀티모달 추천** | <img src="images/multimodal.png" alt="멀티모달 추천 화면" width="400px" /> |
| **추천 페이지** | <img src="images/recommend_page.png" alt="추천 페이지 화면" width="400px" /> |
| **오프라인 매장 안내** | <img src="images/offline_store.png" alt="오프라인 매장 안내 화면" width="400px" /> |
| **마이페이지** | <img src="images/mypage.png" alt="마이페이지 화면" width="400px" /> |

<img src="images/시스템아키텍처다이어그램user.png" alt="시스템 아키텍처 다이어그램 user" />
<br>

## 🤖 인공지능 모델링

- **LLM**: OpenAI GPT-4o-mini  
- **임베딩 모델**: text-embedding-3-small, paraphrase-multilingual-MiniLM-L12-v2  
- **RAG 구조**: Pinecone VectorDB + LLM 조합  
- **멀티에이전트 라우팅**: LangGraph 기반 Supervisor + 전문 에이전트  

<img src="images/챗봇아키텍쳐.jpg" alt="AI 챗봇 아키텍쳐" />

<br>

## 🤖 머신러닝 모델

- **목표**: 영어 description 텍스트로부터 다중 라벨(Main Accord) 예측  
- **모델 계열**: 다국어 임베딩 + 머신러닝 분류기  
- **최종 채택**:  
  - 임베딩: `paraphrase-multilingual-MiniLM-L12-v2` (SentenceTransformer)  
  - 분류기: VotingClassifier (Soft Voting, Logistic Regression + XGBoost)  

👉 MiniLM은 다국어 입력 확장이 가능하고, Soft Voting 앙상블은 단일 모델 대비 안정성과 성능을 개선

- **학습 데이터**: 약 26,000개 (희소·노이즈 라벨 제거 후)  
- **성능**: Micro-F1 ≈ **0.50** (목표 성능 달성)  
- **저장 방식**:  
  - `minilm_model.pt` (임베딩 모델)  
  - `label_info.pkl` (분류기 및 라벨 정보)  

<br>

## 🗄️ VectorDB

- **목적**: LLM과 연동해 향수 추천·FAQ 응답·가격 질의 등을 보조  
- **플랫폼**: Pinecone (AWS us-east-1, Serverless, 1536차원, cosine similarity)  
- **임베딩 모델**: `text-embedding-3-small`  

### 인덱스 구성
- **perfume-vectordb**: 향수 스펙 기반 (802건)  
  - page_content: 향 설명  
  - metadata: 브랜드, 농도, 성별, 계절 점수 등  

- **review-vectordb**: 사용자 리뷰 기반 (6,591건)  
  - page_content: 리뷰 본문  
  - metadata: url + text  

- **keyword-vectordb**: 키워드-어코드 매칭 (53건)  
  - page_content: `"note: Rose | accord: Floral"` 형태 문자열  
  - metadata: id + 원문 텍스트  

<br>

## 📹 시연 동영상

<img src="images/final_demo.png" alt="최종 시연 동영상 링크" />

<br>

## 🚩 기대 효과

- **사용자 편의성**: 전문 지식 없이도 맞춤 향수 선택 가능  
- **데이터 기반 추천**: 인기 순위가 아닌 리뷰·향 설명 기반 추천  
- **시장 가치**: 정보 비대칭 해소, 구매 만족도 및 재구매율 향상  
- **확장성**: 디퓨저, 섬유유연제 등 향 기반 제품군으로 확장 가능  

<br>

## 📢 Contact

- 팀 노션: [Notion](https://www.notion.so/shqkel/SKN14-Final-2-24c9cb46e5e28024a084f0508d66d217?source=copy_link)  
- GitHub 메인 저장소: [Final Repo](https://github.com/skn-ai14-250409/SKN14-Final-2Team)  
- GitHub Django Web: [Web Repo](https://github.com/skn-ai14-250409/SKN14-Final-2Team-Web)  
- GitHub FastAPI: [AI Repo](https://github.com/skn-ai14-250409/SKN14-Final-2Team-Ai)  
=======
### 📢 Contact
- 프로젝트 노션: https://www.notion.so/shqkel/SKN14-Final-2-24c9cb46e5e28024a084f0508d66d217?source=copy_link
- Github SKN14기 저장소: https://github.com/skn-ai14-250409/SKN14-Final-2Team
- Github SKN전체 저장소: https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN14-FINAL-2Team
- **향수 Scentpick** : https://scentpick.store/

>>>>>>> 8d1479cf512c63c46337e233b8d1d59a1ef885c2
