제목: Seong9/scentlab 변경사항을 공동 작업 폴더(scentlab)에 적용

작성일: 2025-09-09

적용 범위
- Seong9에서 개인 작업한 기능(로그인/소셜 로그인(allauth), uauth 프로필, 보호 페이지, 템플릿/정적 리소스)을 공동 작업 폴더의 `scentlab/`에 반영했습니다.

주요 변경 파일/내용 (최신 업데이트 포함)
- `scentlab/scentlab/settings.py`
  - allauth 구성 추가: `django.contrib.sites`, `allauth`, `allauth.account`, `allauth.socialaccount`(+ google/naver/kakao).
  - 로그인 설정: `LOGIN_URL = uauth:login`, `LOGIN_REDIRECT_URL = 'home'`, `LOGOUT_REDIRECT_URL = '/'`.
  - 어댑터 등록: `uauth.adapters.CustomAccountAdapter`, `uauth.adapters.CustomSocialAccountAdapter`.
  - 환경변수 로드: `dotenv`를 사용해 Provider 자격증명 로드, S3 업로드 관련 최소 키 반영.
  - 미들웨어: `allauth.account.middleware.AccountMiddleware` 추가.

- `scentlab/scentlab/urls.py`
  - Seong9 스타일로 루트 라우팅 변경:
    - `''` → `scentpick.views.home`(`home` 이름)
    - `''`에 `scentpick.urls` 포함
    - `accounts/`(allauth), `accounts/login/redirect/`(중간 페이지), `uauth/` 경로 추가
  - admin 경로 제거(현 구성에서는 관리자 페이지 사용하지 않음).

- `scentlab/scentpick/urls.py`
  - `mypage/profile/`, `mypage/password/` 경로 추가.

- `scentlab/scentpick/views.py`
  - `@login_required`로 보호: chat, recommend, perfumes, offlines, mypage.
  - 프로필 수정/비밀번호 변경 뷰 추가.
  - `uauth.utils`(이미지 처리)와 `UserDetail` 의존성 추가.

- `scentlab/uauth/*`
  - models.py: `UserDetail`(name, gender, birth_year, profile_image_url, `avatar_url` 프로퍼티).
  - views.py: 프로필 보완(complete_profile), 로그인(next 지원), 회원가입(유효성+선택적 프로필 이미지 업로드), mypage.
  - urls.py: 로그인/회원가입, 아이디 중복 확인, 소셜 리디렉션 헬퍼, 프로필 보완 경로.
  - adapters.py: 로그인/소셜 로그인 후 `next` 우선 적용.
  - utils.py: Pillow 기반 이미지 처리 + S3 업로드 헬퍼.
  - apps.py + signals.py: User 생성/소셜 가입 시 `UserDetail` 자동 생성/보강.

- 템플릿(`templates/`)
  - `account/login_redirect.html`(소셜 로그인 중간 리디렉션 페이지).
  - `uauth/login.html`, `uauth/register.html`, `uauth/complete_profile.html`.
  - `scentpick/base.html`(Seong9 스타일 네비/사이드 챗봇/토스트 등 반영) 및 `home/chat/recommend/perfumes/offlines/mypage/profile_edit/password_change` 페이지를 보강해 화면이 정상적으로 보이도록 구성.

- 정적 리소스(`static/`)
  - `static/css/scentpick.css`, `static/js/scentpick.js`를 Seong9 인터랙션/레이아웃 기반으로 교체.

Seong9 템플릿 스타일 반영/병합
- `templates/scentpick/base.html`: Seong9 버전으로 교체
  - 상단 네비게이션(고정, 투명 배경/블러), 사용자 메뉴(아바타/메뉴), 사이드 챗봇 토글/패널, 토스트 헬퍼 등을 포함
  - `{% load static %}` 사용, 정적 파일 버전 파라미터 적용(`?v=...`)
- `static/css/scentpick.css`: Seong9의 전체 레이아웃/컴포넌트 스타일로 교체
  - 네비게이션, 컨테이너, 카드, 폼, 그리드, 챗봇, 반응형 등 상세 스타일 포함
- `static/js/scentpick.js`: Seong9의 인터랙션 스크립트로 교체
  - 챗봇 열기/닫기, 메시지 추가, 성별 버튼 active, 필터/태그 active 처리 등
- 로그인/회원가입/프로필 편집 템플릿은 Seong9 스타일 클래스(`auth-container`, `form-group`, `btn-primary` 등)를 사용하도록 유지/정리

화면 표시 문제 해결 내역
- 홈 화면: `templates/scentpick/home.html`을 Seong9 스타일의 `base.html`을 상속하고 히어로 섹션을 노출하도록 구성.
- 소셜 로그인 중간 페이지: `templates/account/login_redirect.html` 스크립트 보강하여 팝업/비팝업 모두 `next`로 이동.
- Chat/Recommend/Perfumes/Offlines/MyPage: 각 페이지 템플릿 생성 및 스타일 적용. `@login_required`가 적용된 페이지들은 비로그인 시 `/uauth/login/?next=...`로 이동함을 확인.
- 네비게이션/정적 리소스: `base.html`에서 `{% static %}` 기반으로 CSS/JS 로드, 상단 네비/챗봇/토스트 정상 출력.

옵션 1(Seong9 1:1 반영) 최신 업데이트
- 템플릿 전면 보강
  - `templates/scentpick/base.html`: Seong9 버전으로 재교체(네비/유저메뉴/챗봇/토스트 포함)
  - `templates/scentpick/product_detail.html`: 상세 페이지 템플릿 추가(노트, 버튼 인터랙션)
  - `templates/socialaccount/login.html`: allauth 소셜 로그인 템플릿 추가(자동 submit)
- 정적 리소스 정합
  - `static/css/scentpick.css`: Seong9 원본 스타일에 맞춰 확장(네비/반응형/챗봇 등 상세)
  - `static/js/scentpick.js`: 챗봇/버튼 active/태그 토글 등 스크립트 이식
- 라우팅/보호 재확인
  - `scentlab/scentlab/urls.py`: Seong9 루트 라우팅(uauth, allauth, home, scentpick.urls)
  - `scentpick/views.py`: 보호 경로(@login_required)와 프로필 편집/비밀번호 변경 정상 동작 확인

남은 확인 목록(환경 의존)
- 소셜 로그인 콘솔의 Redirect URL이 현재 도메인/포트와 일치하는지 확인
- `.env`에 Provider/AWS 키 값 채움(없으면 소셜/업로드 일부 기능 제한)
- DB 스키마 동기화는 준비되면 진행(회원 프로필 이미지 URL 등의 필드 저장 필요 시)

DB 초기화 및 마이그레이션 검증 절차(uauth: `oauth_accounts` 삭제, `users` 컬럼 추가 확인)
- 목적: 새로운 DB에서 마이그레이션을 처음부터 적용하여 최종 스키마가 기대대로 되는지 검증
- 사전: DB 접속 계정에 DROP/CREATE 권한 필요. 현재 DB 설정은 MySQL (`scentpickdb`).

1) 백업(선택)
   - mysqldump -u <USER> -p scentpickdb > backup_scentpickdb.sql

2) DB 삭제/재생성(가장 깔끔)
   - Windows PowerShell 예시
     - mysql -u <USER> -p -e "DROP DATABASE IF EXISTS scentpickdb; CREATE DATABASE scentpickdb DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
   - macOS/Linux 예시
     - mysql -u <USER> -p -e 'DROP DATABASE IF EXISTS scentpickdb; CREATE DATABASE scentpickdb DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;'

3) 마이그레이션 적용
   - python manage.py migrate
   - 기대 결과(uauth): 0001/0002 적용 후 0003에서 `users.profile_image_url` 추가 및 `oauth_accounts` 삭제

4) 검증 쿼리
   - oauth_accounts 존재 여부(없어야 정상)
     - mysql -u <USER> -p -e "USE scentpickdb; SHOW TABLES LIKE 'oauth_accounts';"
   - users에 profile_image_url 존재(있어야 정상)
     - mysql -u <USER> -p -e "USE scentpickdb; SHOW COLUMNS FROM users LIKE 'profile_image_url';"
- 마이그레이션 로그 확인(uauth 0003 포함)
  - mysql -u <USER> -p -e "USE scentpickdb; SELECT app,name FROM django_migrations WHERE app='uauth';"

프로필 이미지 크롭 문제 수정
- 파일: `scentlab/uauth/utils.py`
- 변경: 서버 크롭 함수 `_apply_crop`에서 `scale` 기반 리사이즈를 제거하고, 프론트엔드가 전달한 `(x,y,size)`를 "원본 좌표계" 그대로 사용해 크롭하도록 수정
- 배경: 프론트엔드에서 미리보기 확대 배율 `s`로 나누어 원본 좌표를 전송함. 서버에서 추가로 `scale` 배율로 리사이즈하면 좌표가 어긋나 확대/위치가 틀어지는 문제가 발생
- 효과: 마이페이지 및 네비 아바타에서 설정한 영역이 정확히 저장/표시됨(512x512 정사각, 원형 마스킹은 CSS로 처리)

문제 발생 시 참고
- MySQL 5.7 호환: `ADD COLUMN IF NOT EXISTS` 문법 미지원 이슈는 uauth 0003에서 RunPython으로 회피 적용(컬럼 존재 검사 후 ALTER 수행).
- 여전히 충돌 시, `SHOW COLUMNS FROM users` 결과를 공유해주시면 수정을 반영하겠습니다.

체크리스트
- [ ] `.env`에 Provider 자격증명(GOOGLE_*/NAVER_*/KAKAO_*) 존재 확인
- [ ] (선택) S3 업로드 사용 시 AWS 키/Bucket/Region 설정
- [ ] 로그인 후 `home`, `chat`, `recommend`, `perfumes`, `offlines`, `mypage` 화면 동작 확인

템플릿/정적 리소스 통째 덮어쓰기(Seong9 → 공유)
- 일시: 2025-09-09 15:30:07
- 수행 내용:
  - 기존 백업 생성: `scentlab/templates_backup_YYYYMMDD-HHMMSS`, `scentlab/static_backup_YYYYMMDD-HHMMSS`
  - Seong9/scentlab/templates → scentlab/templates로 전체 복사(클린 미러)
  - Seong9/scentlab/static → scentlab/static로 전체 복사(클린 미러)
- 목적:
  - 화면 레이아웃/스타일/소셜 템플릿까지 Seong9와 1:1 정합 보장
- 확인 포인트:
  - `/` 홈 화면이 Seong9 스타일로 표시(히어로/네비/푸터/챗봇 토글)
  - `/chat`, `/recommend`, `/perfumes`, `/offlines`, `/mypage` 페이지 로드
  - 소셜 로그인 플로우에서 중간 페이지(templates/socialaccount/login.html) 자동 제출 동작
  - 정적 경로가 모두 `{% static %}`로 정상 로드(콘솔 404 없음)


호환/주의 사항
- DB 정합: 코드 기준으로 `users.profile_image_url` 등을 사용합니다. 준비되면 아래로 스키마를 맞춰 주세요.
  - `python manage.py makemigrations uauth`
  - `python manage.py migrate`
  (DB 처리는 나중에 하신다고 하셨으므로, 적용 전까지는 새로운 필드 저장이 반영되지 않을 수 있습니다.)
- 관리자 페이지: 현재 라우팅에서 제외했습니다. 필요 시 `INSTALLED_APPS`에 `django.contrib.admin`을 되살리고, `urls.py`에 경로를 추가하면 됩니다.
- 소셜 자격증명: `.env`에 Provider(client_id/secret)과 AWS 키가 있어야 정상 동작합니다.

의도적으로 변경하지 않은 부분
- 공유 레포의 기존 마이그레이션 파일은 즉시 DB에 영향을 주지 않도록 수정하지 않았습니다(확인 후 스키마 동기화 권장).
- Seong9 작업과 겹치지 않는 기존 템플릿/리소스는 그대로 유지했습니다.

검증 방법
- 비로그인 상태에서 chat/recommend/perfumes/offlines/mypage 접근 → `/uauth/login/?next=...`로 리디렉션.
- `/uauth/login`에서 `next`가 유지되어 로그인 후 원래 페이지로 복귀.
- `/uauth/register`에서 회원가입 시 `UserDetail` 생성, 로그인 후 접근 가능.
