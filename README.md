# Fast API Test Web

FastAPI + PostgreSQL 기반의 간단한 웹 API 프로젝트 🚀

---

## Features

- FastAPI 기반 RESTful API
- PostgreSQL 연동 (Docker Compose)
- Dockerfile + Docker Compose로 손쉽게 배포
- `.env`로 환경변수 안전 관리

---

## Requirements

- **Docker**
- **Docker Compose**

### 설치 필요:  
> [Docker 설치 가이드](https://docs.docker.com/get-docker/)  
> [Docker Compose 설치 가이드](https://docs.docker.com/compose/install/)

---

## How To Run

### 1. '.env'파일 만들기

`.env.example` 참고해서 `.env` 작성:

```
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRES_IN_HOURS=expires_in_hours_value
```

---

### 2. Docker 빌드 & 실행

```bash
$ docker-compose up -d --build
```

---

### 3. 서비스 확인
* FastAPI: http://localhosst
* Swagger Docs: http://localhost/docs

---

## 주요 명령어

| 명령어 | 설명 |
| ------ | ---- |
| `docker-compose up -d --build` | 컨테이너 빌드 & 백그라운드 실행 |
| `docker-compose down` | 모든 컨테이너 종료 및 네트워크 정리 |
| `docker-compose logs -f` | 실시간 로그 모니터링 |
| `docker-compose exec app bash` | 앱 컨테이너 내부 bash 접속 |

---

## DB 모델 변경하기
1. 모델 추가시 models.__init__에 model import 하기
2. 마이그레이션 버전 만들기
```bash
$ alembic revision --autogenerate
```
3. git commit & push

---

## 로그 확인하기
```bash
docker exec -it fastapi_app tail -f /app/logs/app.log

docker exec -it fastapi_app tail -f /app/logs/db.log
```

---

## TODO
* [x] FastAPI 의존성 리팩터
* [x] DB 모델링 및 Alembic 마이그레이션 추가
* [x] ssl 인증서 발급
* [x] 비밀번호, 아이디 유효성 백엔드 추가 검사
* [ ] pytest 테스트 케이스 확장
* [ ] 비동기화
* [ ] db 백업 스케줄
* [ ] 수학 실수 유형 분석 서비스

---