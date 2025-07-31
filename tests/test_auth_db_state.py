# tests/test_auth_db_state.py
from contextlib import contextmanager
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 기존 tests/test_auth.py 의 client, create_user_and_login 재사용
from test_auth import client, create_user_and_login

from config.db import SessionLocal
from models.user import User
from models.refresh_tocken import RefreshToken


@contextmanager
def db_session() -> Session:
    """트랜잭션 롤백을 보장하는 테스트용 세션."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


def test_delete_account_db_state():
    """DELETE /delete_account 호출 시 DB에서도 사용자 레코드가 지워지는지 검증."""
    with create_user_and_login() as (username, *_):
        resp = client.delete("/delete_account")
        assert resp.status_code == 200

    with db_session() as db:
        assert (
            db.query(User).filter(User.username == username).first() is None
        ), "계정 삭제 후에도 사용자 레코드가 남아 있습니다."


def test_refresh_token_revoke_db_state():
    """POST /logout 호출 시 DB의 refresh_token.revoked=True 인지 검증."""
    with create_user_and_login() as (_, _, _, refresh_token):
        resp = client.post("/logout", cookies={"refresh_token": refresh_token})
        assert resp.status_code == 200

    with db_session() as db:
        db_token = (
            db.query(RefreshToken).filter(RefreshToken.token == refresh_token).with_for_update().first()
        )
        assert db_token is not None, "로그아웃 후에도 RefreshToken 레코드가 없습니다."
        assert (
            db_token.revoked is True
        ), "로그아웃 시 refresh_token.revoked가 True가 아닙니다."


def test_register_and_cleanup_db_state():
    """POST /register 로 사용자 생성 → 직접 DB에서 삭제 → 레코드 삭제 확인."""
    username = f"user-{uuid.uuid4().hex[:8]}"
    password = "test1234!"

    # 1) API로 회원가입
    resp = client.post("/register", json={"username": username, "password": password})
    assert resp.status_code == 201

    # 2) DB에 레코드 생성 확인
    with db_session() as db:
        assert db.query(User).filter(User.username == username).count() == 1

    # 3) 직접 삭제
    with db_session() as db:
        user = db.query(User).filter(User.username == username).first()
        assert user is not None
        db.delete(user)
        db.commit()

    # 4) 삭제 후 확인
    with db_session() as db:
        assert (
            db.query(User).filter(User.username == username).count() == 0
        ), "직접 삭제 후에도 레코드가 남아 있습니다."
