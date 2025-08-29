# SKN14-Final-2Team
Repository for SKN14-Final-2Team

### ☘️팀명: ScentLab
### 🌳홈페이지: ScentPick

## **🧴ScentPick: LLM 기반으로 맞춤형 향수를 추천하는 대화형 챗봇 서비스**


>사용자가 원하는 조건(향수 노트, 분위기, 계절감 등)에 맞추어 향수를 추천해주는 서비스를 제공합니다!

`ScentPick` <br>
1. 기존 향수 구매할 때 발생하는 문제점에는 낮은 시향 접근성 및 지속력·발향력·성분·계절 적합성 등 구체적인 정보를 얻기 어려운 점이 있습니다. 
2. 또한 수많은 브랜드 제품 중에서 자신의 취향에 맞는 향을 찾기 어렵고, 전문 용어 위주의 노트 설명은 일반 소비자가 이해하기 어려워 원하는 향이 실제로 어떤 향기인지 파악하기 힘든 실정입니다. 
3. 그래서 이러한 문제 해결을 위해 챗봇을 통해 사용자가 원하는 향을 분석하고 맞춤형 향수를 추천하는 서비스를 제공하는 것을 목표로 합니다.
<br><br>`RAG`과 `VectorDB` 를 활용한 챗봇서비스 `ScentPick`으로 다양한 향수 추천 기능을 테스트할 수 있습니다. <br><br>

<img width="896" height="726" alt="Image" src="https://github.com/user-attachments/assets/3c0233f2-cf6e-4644-b9f5-eac7d1f34421" />




## 🎇 Features 🎇
- **RAG기반의 Chatbot** : 
    - RAG 기술로 향수 브랜드 전체 데이터베이스에서 필요한 부분을 가져오는 기능 
    - 로그인한 고객 대상으로 채팅 히스토리를 제공하는 기능 
    - 실시간으로 고객과 챗봇의 질의응답 대화가 가능
      
- **사용자의 의견을 반영한 추천 시스템** :
    - 사용자가 원하는 노트와 향 종류를 반영하여 적절한 향수 제품을 추천하는 기능
      
- **간결하고 직관적인 UI** 

---

## 🛠 Tech Stack

- 개발 환경: Pycharm, VSCode
- 기술 스택: Pandas, OpenAI, Pinecone, Langchain, Selenium, django

    ![html5](https://img.shields.io/badge/html5-E34F26?style=flat-square&logo=html5&logoColor=white)
    ![css](https://img.shields.io/badge/css-663399?style=flat-square&logo=css&logoColor=white) 
    ![javascript](https://img.shields.io/badge/javascript-F7DF1E?style=flat-square&logo=javascript&logoColor=white)
    ![figma](https://img.shields.io/badge/figma-F24E1E?style=flat-square&logo=figma&logoColor=white)

- **Server** : <br>
    ![amazonwebservices](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)
    ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)

- **LLM Application** : <br>
    ![LangGraph](https://img.shields.io/badge/LangGraph-000000?style=flat-square&logo=langgraph&logoColor=white)
    ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)


---

## 📝 Table of Content

- 팀원소개
- ScentPick 챗봇서비스 소개
- 주요 기능
- Requirements
- 시스템 아키텍처
- 데이터 구조
- 기대 효과 
- Contact

---

## 팀원 소개


| 이름   | GitHub ID      | 업무                                                  |
|------|----------------|-----------------------------------------------------|
| 박빛나  | ParkVitna      | PM, 프로젝트 관리, 데이터 크롤링 및 정제, 프로젝트 기획서 작성, django ORM  | 
| 유용환  | yooyonghwan111 | RM, vector DB 구축, wbs 작성, 데이터 조회 프로그램 작성            | 
| 한성규  | Seonggyu-Han   | 향수 데이터 수집, 전처리, api 조사, 데이터베이스 설계문서  작성             |
| 강윤구  | dbsrn09        | 향수 데이터 크롤링, 정제, 챗봇 사용자 입력 전처리                       | 
| 정유진  | rainbow0291    | UI 구성, 화면 설계 및 기능 구체화 , README 파일, 회의록, 요구사항 정의서 작성 | 

---

## 🧴ScentPick 챗봇서비스 소개

- 사용자가 원하는 조건에 맞게 향수를 3가지 추천해주는 챗봇 구현
- 향수 이름, 향수 브랜드, 향수 종류, 향 설명, 가격, 용량, 메인 어코드, 탑/미들/베이스 노트 데이터를 DB에 저장
- 참고 링크
<img width="1427" height="679" alt="Image" src="https://github.com/user-attachments/assets/1e4b6971-1b67-4fb8-b028-5573b7c274de" />
---

## 📱 주요 기능
- **즐겨찾기** 기능: 로그인한 경우 마이페이지에 선택한 향수를 표시하는 기능
- **챗봇추천** 기능: 사용자가 작성한 조건에 맞게 3가지 향수를 추천해주는 기능
- 링크: 추천된 향수이름을 클릭하면 해당 제품 **상세페이지**로 연결되는 기능
- 로그인하고 마이페이지에서 챗봇과 **대화내역**chat history  저장, 표시되는 기능
- 향 설명, 탑/미들/베이스 노트, 가격, 용량 등의 **정보를 제공**하는 기능
- **평점 리뷰 제공**하는 기능
- 사용자 인증 및 로그인 시간 기록
- 향수/노트/어코드/브랜드/가격/이미지 등 도메인 엔터티 관리
- RAG 검색을 위한 임베딩/소스 문서 관리

<img width="1068" height="599" alt="Image" src="https://github.com/user-attachments/assets/bb77a9bd-213f-4f8c-8779-c70a985c2340" />
<img width="1072" height="591" alt="Image" src="https://github.com/user-attachments/assets/dda1392d-caa3-404e-9f33-6a0b7d155d18" />
<img width="473" height="284" alt="Image" src="https://github.com/user-attachments/assets/d8a3b79b-8001-42a4-95f9-777174a41153" />
<img width="958" height="474" alt="Image" src="https://github.com/user-attachments/assets/8bcac447-f498-4817-a4f9-011cd2c4b179" />

---

## 🛠 Requirements

- Selenium
- OpenAI
- python-dotenv
- webdriver-manager
- tqdm
- pandas 
- django
---

## 🖥️시스템 아키텍처 
- 데이터 허브: 스크래핑으로 수집한 향수·노트·가격·리뷰·이미지 원천을 정규화해 저장
- 추천 근거 저장: 대화 중 사용된 후보/점수/근거 문장(소스 링크) 보존 → 재현 가능성 확보
- 개인화: 사용자 즐겨찾기/리뷰/대화 로그 기반 개인화


#### **데이터베이스 구조**

**1. 관계형 DB (MySQL)**
- 기준 마스터(향수/브랜드/어코드), 관계 테이블, 사용자/세션/대화/즐겨찾기/가격

- 벡터 저장소 (Pinecone : 향 설명·리뷰 요약 임베딩, 인덱스/버전 관리
- RDB에는 벡터 ID/버전만 참조, 원문 텍스트는 규격화 테이블과 함께 관리

**2. 적용한 데이터베이스**
  - AWS의 RDS를 기반으로 MySQL DB를 적용함.
  - perfumes의 필요 칼럼들 / 키워드 사전을 PineconeDB에 벡터화 하여 저장함.
  - 전체 문서는 MySQL에 저장

---

## 🔢데이터 구조 

<img width="1345" height="893" alt="Image" src="https://github.com/user-attachments/assets/860be6e9-2cf1-4d50-afd5-92bec117a181" />

---

## 🚩기대 효과


- 향수 데이터가 카테고리별로 구분되어 있어 사용자들이 보다 편리하게 자신의 기호에 맞는 향수를 찾아볼 수 있음
- Database에서 조건에 맞는 향수를 필터링한 결과를 손쉽게 얻을 수 있음
- 오늘의 추천 기능으로 계절감, 날씨상황을 반영한 향수를 추천 가능
- 자신의 취향에 맞는 향수를 찾고, 고객 만족도와 재구매율도 증가할 것으로 기대됨
- 향수 구매시 시향이 어려울 때 챗봇 추천으로 고객 편의성 증대


---

## 📢 Contact
- 프로젝트 노션: https://www.notion.so/shqkel/SKN14-Final-2-24c9cb46e5e28024a084f0508d66d217?source=copy_link
- Github 저장소: https://github.com/skn-ai14-250409/SKN14-Final-2Team
-               https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN14-FINAL-2Team

