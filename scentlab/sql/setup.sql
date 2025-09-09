-- Active: 1753665100890@@127.0.0.1@3306@scentpickdb
-- Active: 1753665113642@@127.0.0.1@3306@mysql
# root계정으로 실행
# 모든 host에서 접근가능한 django계정 생성 -> 이미 했으면 실행X
create user 'django'@'%' identified by 'django';

# qnadb 생성
create database scentpickdb character set utf8mb4 collate utf8mb4_unicode_ci;

# django 사용자에게 scentpickdb 권한 부여
grant all privileges on scentpickdb.* to 'django'@'%';
flush privileges;

# models.py 변경 후 migration 안될 때
-- # scentpick 앱만 롤백
-- python manage.py migrate scentpick zero

-- # (선택) scentpick/migrations/ 폴더의 마이그레이션 파일들을 __init__.py 빼고 삭제

-- # 새 마이그레이션 생성 후 적용
-- python manage.py makemigrations
-- python manage.py migrate