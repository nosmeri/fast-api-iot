import uuid
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from config.db import SessionLocal
from models.user import User
from models.refresh_tocken import RefreshToken

client = TestClient(app)


@contextmanager
def db_session() -> Session:
    """테스트용 DB 세션(자동 롤백)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # 변경사항 무효화
        db.close()


def _create_user(username: str, password: str) -> None:
    client.post("/register", json={"username": username, "password": password})


def test_delete_account_db_state():
    """계정 삭제 후 DB에 사용자 레코드가 남아 있지 않은지 검증."""
    username = f"user-{uuid.uuid4().hex[:8]}"
    password = "test1234!"
    _create_user(username, password)

    # 로그인 후 쿠키 세팅
    client.post("/login", json={"username": username, "password": password})

    # 삭제 요청
    delete_resp = client.delete("/delete_account")
    assert delete_resp.status_code == 200

    # --- DB 상태 검증 ---
    with db_session() as db:
        db_user = db.query(User).filter(User.username == username).first()
        assert db_user is None, "사용자 삭제 후 DB에 레코드가 남아 있습니다."


def test_refresh_token_revoke_db_state():
    """로그아웃 시 refresh token이 DB에서 revoke=True 로 변경되는지 검증."""
    username = f"user-{uuid.uuid4().hex[:8]}"
    password = "test1234!"
    _create_user(username, password)

    login_resp = client.post(
        "/login", json={"username": username, "password": password}
    )
    refresh_token = login_resp.cookies.get("refresh_token")
    assert refresh_token, "refresh_token 쿠키가 없습니다."

    # 로그아웃
    logout_resp = client.post("/logout")
    assert logout_resp.status_code == 200

    # --- DB 상태 검증 ---
    with db_session() as db:
        db_token = (
            db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        )
        assert db_token is not None, "RefreshToken 레코드가 없습니다."
        assert (
            db_token.revoked is True
        ), "로그아웃 후에도 revoked 플래그가 False 입니다."


def test_register_commit_and_rollback():
    """회원가입 후 커밋되어 존재하다가, 롤백으로 테스트 DB 가 깨끗해지는지 확인."""
    username = f"user-{uuid.uuid4().hex[:8]}"
    password = "test1234!"

    # 회원가입
    resp = client.post("/register", json={"username": username, "password": password})
    assert resp.status_code == 201

    # 세션 1: 커밋 확인
    with db_session() as db:
        assert db.query(User).filter(User.username == username).count() == 1

    # 세션 2: 롤백 확인 (db_session() 의 rollback 덕분에 항상 깨끗해야 함)
    with db_session() as db:
        db.query(User).filter(User.username == username).delete()
        db.commit()

    with db_session() as db:
        assert (
            db.query(User).filter(User.username == username).count() == 0
        ), "롤백 후에도 레코드가 남아 있습니다."
