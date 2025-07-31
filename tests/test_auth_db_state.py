# tests/test_auth_db_state.py
import uuid
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 기존 테스트 파일에서 재사용
from tests.test_auth import create_user_and_login  # 경로는 프로젝트 구조에 맞게 조정
from main import app
from config.db import SessionLocal
from models.user import User
from models.refresh_tocken import RefreshToken

client = TestClient(app)


@contextmanager
def db_session() -> Session:
    """트랜잭션 롤백을 보장하는 테스트용 세션."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


# --------- 테스트 케이스들 ---------


def test_delete_account_db_state():
    """계정 삭제 후 DB에서 사용자 레코드가 사라졌는지 검증."""
    with create_user_and_login() as (username, password, *_):
        # 계정 삭제
        resp = client.delete("/delete_account")
        assert resp.status_code == 200

    # DB 상태 확인
    with db_session() as db:
        assert (
            db.query(User).filter(User.username == username).first() is None
        ), "사용자 삭제 후에도 레코드가 남아 있습니다."


def test_refresh_token_revoke_db_state():
    """로그아웃 시 refresh_token.revoked=True 로 바뀌는지 검증."""
    with create_user_and_login() as (_, _, _, refresh_token):
        # 로그아웃
        resp = client.post("/logout")
        assert resp.status_code == 200

    # DB 상태 확인
    with db_session() as db:
        db_token = (
            db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        )
        assert db_token is not None, "RefreshToken 레코드가 없습니다."
        assert db_token.revoked is True, "revoked 플래그가 True 가 아닙니다."


def test_register_commit_and_rollback():
    """회원가입 → 커밋 확인 → 롤백으로 DB 청결 확인."""
    # 새 사용자 생성
    with create_user_and_login() as (username, _, *_):
        # 세션 1: 커밋 상태
        with db_session() as db:
            assert db.query(User).filter(User.username == username).count() == 1

    # 세션 2: 롤백 후에도 레코드가 없어야 함
    with db_session() as db:
        assert (
            db.query(User).filter(User.username == username).count() == 0
        ), "롤백 후에도 레코드가 남아 있습니다."
