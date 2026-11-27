from uuid import uuid4

from app.core.passwords import hash_password, verify_password
from app.core.sessions import (
    create_csrf_token,
    create_session_token,
    read_session_token,
    validate_csrf_token,
)


def test_argon2_password_hash_verifies_only_matching_password() -> None:
    password_hash = hash_password("a-long-local-staff-password")
    assert password_hash.startswith("$argon2")
    assert verify_password("a-long-local-staff-password", password_hash)
    assert not verify_password("a-different-password", password_hash)


def test_password_policy_rejects_short_passwords() -> None:
    try:
        hash_password("short")
    except ValueError as exc:
        assert "12 characters" in str(exc)
    else:
        raise AssertionError("Expected short passwords to be rejected")


def test_signed_session_token_round_trips_user_id() -> None:
    user_id = uuid4()
    token = create_session_token(user_id)
    assert read_session_token(token) == user_id
    assert read_session_token(token + "tampered") is None


def test_csrf_token_is_bound_to_the_authenticated_user() -> None:
    user_id = uuid4()
    token = create_csrf_token(user_id)
    assert validate_csrf_token(user_id, token)
    assert not validate_csrf_token(uuid4(), token)
    assert not validate_csrf_token(user_id, token + "tampered")
