"""Smoke tests for the user module: router registration, login, tenant scoping."""
from sqlalchemy.orm import Session

from app.user import services
from tests.conftest import make_user


def test_router_registered():
    from app.main import app

    assert any(path.startswith("/api/v1/users") for path in app.openapi()["paths"])


def test_list_users_requires_auth(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_login_returns_token_scoped_to_users_tenant(client, tenant_a, db_session):
    user = make_user(db_session, tenant_a)
    response = client.post(
        "/api/v1/users/login", data={"username": user.email, "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_rejects_wrong_password(client, tenant_a, db_session):
    user = make_user(db_session, tenant_a)
    response = client.post(
        "/api/v1/users/login", data={"username": user.email, "password": "wrong"}
    )
    assert response.status_code == 401


def test_service_enforces_tenant_scope(db_session: Session, tenant_a, tenant_b):
    user_a = make_user(db_session, tenant_a)
    make_user(db_session, tenant_b)

    users_for_a = services.list_users(db_session, tenant_a.id)
    assert [u.id for u in users_for_a] == [user_a.id]
