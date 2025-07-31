# Fast API I.o.T.

FastAPI + PostgreSQL 기반의 간단한 웹 API 프로젝트 🚀

---

## Features

- **FastAPI** 기반 RESTful API
- **PostgreSQL** 연동 (Docker Compose)
- **JWT 인증** 시스템 (Access Token + Refresh Token)
- **사용자 관리** (회원가입, 로그인, 비밀번호 변경)
- **관리자 기능** (사용자 관리, 권한 설정)
- **유효성 검사** (백엔드/프론트엔드 동기화)
- **Docker** + **Docker Compose**로 손쉽게 배포
- **Alembic** 데이터베이스 마이그레이션
- **로깅 시스템** (앱 로그, DB 로그 분리)

---

## Requirements

- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)

### 설치 필요:  
> [Docker 설치 가이드](https://docs.docker.com/get-docker/)  
> [Docker Compose 설치 가이드](https://docs.docker.com/compose/install/)

---

## How To Run

### 1. '.env'파일 만들기

`.env.example` 참고해서 `.env` 작성:

```env
# PostgreSQL 설정
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db

# JWT 설정
JWT_SECRET_KEY=your_jwt_secret_key_here_make_it_long_and_random
JWT_ALGORITHM=HS256
JWT_EXPIRES_IN_HOURS=24
JWT_REFRESH_EXPIRES_IN_DAYS=30

# 데이터베이스 URL (자동 생성됨)
SQLALCHEMY_DATABASE_URL=postgresql://your_username:your_password@postgres:5432/your_db
```

### 2. Docker 빌드 & 실행

```bash
# 컨테이너 빌드 및 백그라운드 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

### 3. 서비스 확인
- **FastAPI**: http://localhost
- **Swagger Docs**: http://localhost/docs (관리자 권한 필요)
- **ReDoc**: http://localhost/redoc (관리자 권한 필요)

---

## 주요 명령어

| 명령어 | 설명 |
| ------ | ---- |
| `docker-compose up -d --build` | 컨테이너 빌드 & 백그라운드 실행 |
| `docker-compose down` | 모든 컨테이너 종료 및 네트워크 정리 |
| `docker-compose logs -f` | 실시간 로그 모니터링 |
| `docker-compose exec app bash` | 앱 컨테이너 내부 bash 접속 |
| `docker-compose restart app` | 앱 컨테이너만 재시작 |

---

## 프로젝트 구조

```
app/
├── alembic/              # 데이터베이스 마이그레이션
├── config/               # 설정 파일
├── models/               # SQLAlchemy 데이터베이스 모델
├── routers/              # FastAPI 라우터
├── schemas/              # Pydantic API 스키마
├── services/             # 비즈니스 로직
├── static/               # 정적 파일 (CSS, JS)
├── templates/            # HTML 템플릿
├── utils/                # 유틸리티 함수
└── main.py               # 애플리케이션 진입점
```

---

## API 엔드포인트

### 인증/사용자 관련
- `GET /login` - 로그인 페이지
- `POST /login` - 로그인 처리
- `GET /register` - 회원가입 페이지
- `POST /register` - 회원가입 처리
- `GET /changepw` - 비밀번호 변경 페이지
- `PUT /changepw` - 비밀번호 변경 처리
- `POST /logout` - 로그아웃
- `GET /validation-rules` - 유효성 검사 규칙
- `DELETE /delete_account` - (본인) 계정 삭제

### 파일/기타
- `POST /upload` - 파일 업로드
- `GET /health` - 헬스체크 (문서 미포함)

### 관리자 기능
- `GET /admin` - 관리자 페이지
- `PUT /admin/user` - 사용자 정보 수정
- `DELETE /admin/user` - 사용자 삭제

### 기타
- `GET /` - 메인 페이지
- `GET /mypage` - 마이페이지

### 문서
- `GET /docs` - Swagger UI (관리자만)
- `GET /redoc` - ReDoc (관리자만)
- `GET /openapi.json` - OpenAPI 스키마 (관리자만)

---

## DB 모델 변경하기

1. **모델 추가시** `models/__init__.py`에 model import 하기
2. **마이그레이션 버전 만들기**
```bash
docker-compose exec app alembic revision --autogenerate -m "설명"
```
3. **git commit & push**

---

## 로그 확인하기

```bash
# 앱 로그 실시간 확인
docker exec -it fastapi_app tail -f /app/logs/app.log

# DB 로그 실시간 확인
docker exec -it fastapi_app tail -f /app/logs/db.log

# Docker Compose로 로그 확인
docker-compose logs -f app
```

---

## 개발 팁

### 환경변수 변경 시
```bash
# 컨테이너 재시작
docker-compose restart app
```

### 코드 변경 시
```bash
# 컨테이너 재빌드
docker-compose up -d --build
```

### 데이터베이스 초기화
```bash
# 컨테이너와 볼륨 모두 삭제
docker-compose down -v
docker-compose up -d --build
```

---

## 백업 스크립트 (`scripts/backup.sh`)

### Crontab 등록 (자동 실행)
```bash
crontab -e
```
```
0 3 * * * /home/nosmeri/fast-api-testweb/scripts/backup.sh >> /home/nosmeri/db_backups/backup.log 2>&1
```

### 사전 준비사항
- `~/db_backups` 디렉토리 미리 생성
  ```bash
  mkdir -p ~/db_backups
  chmod +x scripts/backup.sh
  ```

---

## 코드 스타일 자동화

이 프로젝트는 코드 스타일 자동화를 권장합니다.

- **Black**: 코드 자동 포매팅
- **isort**: import 정렬
- **autoflake**: 사용하지 않는 import/변수 자동 삭제

### 설치
```bash
pip install black isort autoflake
```

### 전체 적용
```bash
black .
isort .
autoflake --remove-all-unused-imports --in-place -r .
```

### VSCode 등 에디터에서 저장 시 자동 적용 가능

---

## TODO

### 완료 ✅
- [x] FastAPI 의존성 리팩터링
- [x] DB 모델링 및 Alembic 마이그레이션 추가
- [x] SSL 인증서 발급
- [x] 비밀번호, 아이디 유효성 백엔드 추가 검사
- [x] JWT 토큰 시스템 구현
- [x] 사용자 관리 기능
- [x] 관리자 기능
- [x] 프론트엔드/백엔드 유효성 검사 동기화
- [x] 코드 중복 제거 및 모듈화
- [x] pytest 오류 고치기

### 진행 중 🔄
- [ ] pytest 테스트 케이스 확장
- [ ] 비동기화 개선
- [ ] DB 백업 스케줄

### 계획 📋
- [ ] 로그 개선
- [ ] API 문서화 개선
- [ ] 성능 모니터링 추가
- [ ] CSRF 토큰 추가

---

## 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

MIT License는 다음과 같은 특징이 있습니다:

- ✅ **자유로운 사용**: 상업적/개인적 사용 모두 가능
- ✅ **수정 및 배포**: 코드 수정, 배포, 판매 가능  
- ✅ **최소한의 제약**: 원본 라이선스와 저작권 고지만 유지하면 됨
- ❌ **책임 면제**: 개발자는 어떠한 책임도 지지 않음

자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request