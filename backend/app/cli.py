import argparse
from getpass import getpass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.passwords import hash_password
from app.db.models import User
from app.infrastructure.database import engine


def create_staff(email: str, display_name: str, role: str) -> None:
    normalized_email = email.strip().casefold()
    if not normalized_email or "@" not in normalized_email:
        raise SystemExit("A valid staff email is required.")
    if not display_name.strip():
        raise SystemExit("A non-empty display name is required.")

    password = getpass("New staff password (minimum 12 characters): ")
    confirm = getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("Passwords do not match.")

    try:
        password_hash = hash_password(password)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    with Session(engine) as session, session.begin():
        existing = session.scalar(
            select(User).where(func.lower(User.email) == normalized_email)
        )
        if existing is not None:
            raise SystemExit(
                "An account with this email already exists; automatic account linking is disabled."
            )
        session.add(
            User(
                auth_provider=None,
                provider_subject=None,
                email=normalized_email,
                display_name=display_name.strip()[:150],
                password_hash=password_hash,
                role_codes=[role],
                account_status="ACTIVE",
            )
        )
    print(f"Created local staff account {normalized_email} with role {role}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="ST-NLP local administration CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    staff = subparsers.add_parser("create-staff", help="Create a local staff account")
    staff.add_argument("--email", required=True)
    staff.add_argument("--display-name", required=True)
    staff.add_argument("--role", choices=("ADMIN", "RECEIVER"), required=True)
    args = parser.parse_args()

    if args.command == "create-staff":
        create_staff(args.email, args.display_name, args.role)


if __name__ == "__main__":
    main()
