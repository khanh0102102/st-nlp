import argparse
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import User
from app.infrastructure.database import engine
from app.ml.training import train_registered_model


def main() -> None:
    parser = argparse.ArgumentParser(description="ST-NLP model training CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    train = sub.add_parser("train", help="Train one model on a frozen dataset")
    train.add_argument("--dataset-id", required=True)
    train.add_argument("--model-family", choices=("NB", "SVM", "CNN_1D", "LSTM"), required=True)
    train.add_argument("--created-by", required=True, help="UUID of an active ADMIN user")
    train.add_argument("--seed", type=int, default=42)
    train.add_argument("--epochs", type=int, default=15)
    args = parser.parse_args()

    with Session(engine, expire_on_commit=False) as session:
        user = session.get(User, UUID(args.created_by))
        if user is None or user.account_status != "ACTIVE" or "ADMIN" not in set(user.role_codes or []):
            raise SystemExit("--created-by must be the UUID of an active ADMIN user.")
        version = train_registered_model(
            session=session,
            dataset_id=UUID(args.dataset_id),
            model_family=args.model_family,
            created_by=user.id,
            random_seed=args.seed,
            epochs=args.epochs,
        )
        print(
            f"Training completed: model_version={version.id} "
            f"family={version.model_family} version={version.version_label} "
            f"status={version.model_status}"
        )


if __name__ == "__main__":
    main()
