## SKN14-Final-2Team
Repository for SKN14-Final-2Team

### ☘️팀명: ScentLab
### 🌳홈페이지: ScentPick (https://scentpick.store)

### **🧴ScentPick: LLM 기반으로 맞춤형 향수를 추천하는 대화형 챗봇 서비스**


>사용자가 원하는 조건(향수 노트, 분위기, 계절감 등)에 맞추어 향수를 추천해주는 서비스를 제공합니다!

`ScentPick` <br>
1. 기존 향수 구매할 때 발생하는 문제점에는 낮은 시향 접근성 및 지속력·발향력·성분·계절 적합성 등 구체적인 정보를 얻기 어려운 점이 있습니다. 
2. 또한 수많은 브랜드 제품 중에서 자신의 취향에 맞는 향을 찾기 어렵고, 전문 용어 위주의 노트 설명은 일반 소비자가 이해하기 어려워 원하는 향이 실제로 어떤 향기인지 파악하기 힘든 실정입니다. 
3. 그래서 이러한 문제 해결을 위해 챗봇을 통해 사용자가 원하는 향을 분석하고 맞춤형 향수를 추천하는 서비스를 제공하는 것을 목표로 합니다.
<br><br>`LLM`과 `Multimodal`, `VectorDB` 를 활용한 챗봇서비스 `ScentPick`으로 다양한 향수 추천 기능을 테스트할 수 있습니다. <br><br>

<img width="896" height="726" alt="Image" src="https://github.com/user-attachments/assets/3c0233f2-cf6e-4644-b9f5-eac7d1f34421" />

### 🎇 Features 🎇
- **RAG기반의 Chatbot** : 
    - RAG 기술로 향수 브랜드 전체 데이터베이스에서 필요한 부분을 가져오는 기능 
    - 로그인한 고객 대상으로 채팅 히스토리를 제공하는 기능 
    - 실시간으로 고객과 챗봇의 질의응답 대화가 가능
    - 이미지 업로드하면 분위기에 맞는 향수를 추천하는 **멀티모달** 기능  
- **사용자의 의견을 반영한 추천 시스템** :
    - 사용자가 원하는 노트와 향 종류를 반영하여 적절한 향수 제품을 추천하는 기능
      
- **간결하고 직관적인 UI** 


### 🛠 Tech Stack

- 개발 환경: Pycharm, VSCode
- 기술 스택
<img width="826" height="353" alt="Image" src="https://github.com/user-attachments/assets/07c03098-faf3-4959-8e24-980fc9cece3f" />

- **Backend**: 
  - Python, FastAPI, Uvicorn
  - AWS Elastic Beanstalk, Docker 
- **Frontend**: 
  - Django, HTML5, CSS3, JavaScript, Figma
- **Data**:
  - Selenium, Webdriver, Pandas, Numpy
- **AI/ML** : 
  - OpenAI GPT(LLM, 4o-mini),LangChain, LangGraph, 
  - HuggingFace Transformers(XLM-RoBERTa)
- **Database** : 
  - MySQL (AWS RDS), Pinecone Vector DB
- **Server** : 
  - AWS, MySQL   
- **DevOps**: 
  - Github, CI/CD, AWS 



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




### 🖥️시스템 아키텍처  <br>

<img width="1911" height="651" alt="Image" src="https://github.com/user-attachments/assets/f4830031-5058-4767-ac3a-aaab4dbe9c36" />

<img width="655" height="464" alt="Image" src="https://github.com/user-attachments/assets/624ce6a7-12a7-41b7-9b44-1768c083929e" /> <br>
- LLM_parser         : 2개 이상의 다중 제품 속성(facets) 쿼리를 파싱/정규화.
- FAQ_agent          : 향수 지식/정의/차이/일반 질문.
- human_fallback     : 비(非)향수 또는 오프토픽.
- price_agent        : 가격 전용 의도(cheapest, price, buy, discount 등).
- ML_agent           : 단일 취향/무드 추천 및 최근 추천 결과에 대한 FOLLOW-UP.
- memory_echo        : 사용자가 "방금 내가 뭐라고 했지?" / 마지막 질문을 묻는 경우.
- rec_echo           : 사용자가 "네가 방금 추천한 목록/이름 다시 보여줘"를 요청하는 경우.

- 데이터 허브: 스크래핑으로 수집한 향수·노트·리뷰·이미지 원천을 정규화해 저장
- 추천 근거 저장: 대화 중 사용된 후보/점수/근거 문장(소스 링크) 보존 → 재현 가능성 확보
- 개인화: 사용자 즐겨찾기/리뷰/대화 로그 기반 개인화


### **데이터베이스 구조**

**1. 관계형 DB (MySQL)**
- 기준 마스터(향수/브랜드/어코드), 관계 테이블, 사용자/세션/대화/즐겨찾기
- 벡터 저장소 (Pinecone) : 향 설명·리뷰 요약 임베딩, 인덱스/버전 관리
- RDB에는 벡터 ID/버전만 참조, 원문 텍스트는 규격화 테이블과 함께 관리

**2. 적용한 데이터베이스**
  - AWS의 RDS를 기반으로 MySQL DB를 적용함.
  - perfumes의 필요 칼럼들 / 키워드 사전을 PineconeDB에 벡터화 하여 저장함.
  - 전체 문서는 MySQL에 저장


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


- **향후 계획**
- 데이터 보강: 영어 리뷰 코퍼스 수집 → 라벨링 반자동화(키워드 부트스트랩 + 휴먼 검수)
- Text augmentation: back-translation/EDA로 저빈도 라벨 보강
- 모델 개선: mDeBERTa-v3 / XLM-R-large 실험, Prompt-tuning/LoRA 경량 파인튜닝
- 임계값 학습형: 라벨-별 temperature/threshold를 검증 셋 학습으로 최적화

### 시스템 통합
- FastAPI 백엔드 개발
- DB와 모델 연동, API 엔드포인트 구현
- CI/CD, AWS  Elastic Beanstalk 배포
- 통합 테스트 , 전체 기능 통합 및 오류 수정

### 최종 개발
- 소스코드 정리 및 문서화
- 산출물(결과보고서 등) 업데이트 및 리소스 정리
- 발표자료 정리 및 최종 발표(10/2)

---

### 🚩기대 효과


- 향수 데이터가 카테고리별로 구분되어 있어 사용자들이 보다 편리하게 자신의 기호에 맞는 향수를 찾아볼 수 있음
- Database에서 조건에 맞는 향수를 필터링한 결과를 손쉽게 얻을 수 있음
- 오늘의 추천 기능으로 계절감, 날씨상황을 반영한 향수를 추천 가능
- 자신의 취향에 맞는 향수를 찾고, 고객 만족도와 재구매율도 증가할 것으로 기대됨
- 향수 구매시 시향이 어려울 때 챗봇 추천으로 고객 편의성 증대

---

### 📢 Contact
- 프로젝트 노션: https://www.notion.so/shqkel/SKN14-Final-2-24c9cb46e5e28024a084f0508d66d217?source=copy_link
- Github SKN14기 저장소: https://github.com/skn-ai14-250409/SKN14-Final-2Team
- Github SKN전체 저장소: https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN14-FINAL-2Team
- **향수 Scentpick** : https://scentpick.store/

