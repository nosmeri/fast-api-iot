import uuid

from conftest import client, create_user_and_login, db_session
from models.refresh_tocken import RefreshToken  # type: ignore
from models.user import User  # type: ignore


def test_delete_account_db_state():
    with create_user_and_login() as (username, *_):
        resp = client.delete("/delete_account")
        assert resp.status_code == 200

    with db_session() as db:
        assert (
            db.query(User).filter(User.username == username).first() is None
        ), "계정 삭제 후에도 사용자 레코드가 남아 있습니다."


def test_refresh_token_revoke_db_state():
    with create_user_and_login() as (_, _, _, refresh_token):
        resp = client.post("/logout")
        assert resp.status_code == 200

    with db_session() as db:
        db_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.token == refresh_token)
            .with_for_update()
            .first()
        )
        assert db_token is not None, "로그아웃 후에도 RefreshToken 레코드가 없습니다."
        db.refresh(db_token)
        assert (
            db_token.revoked is True
        ), "로그아웃 시 refresh_token.revoked가 True가 아닙니다."


def test_register_and_cleanup_db_state():
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
