from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import IncidentCategory
from app.infrastructure.database import engine

CATEGORIES = (
    ("ROAD_BRIDGE_INFRA_DAMAGE", "Đường/Cầu/Hạ tầng hư hỏng",
     "Hư hỏng vật lý của đường, cầu và hạ tầng giao thông đô thị.", 1),
    ("POWER_LIGHTING", "Điện lực/Chiếu sáng",
     "Sự cố điện lực và hệ thống chiếu sáng công cộng.", 2),
    ("DRAINAGE_SEWER", "Cống/Hố ga/Thoát nước",
     "Sự cố cống, hố ga và hệ thống thoát nước.", 3),
    ("SIDEWALK_ROADWAY", "Vỉa hè/Lòng đường",
     "Vấn đề liên quan không gian, mặt bằng và việc sử dụng vỉa hè/lòng đường.", 4),
    ("TREES_OBSTRUCTIONS", "Cây xanh/Vật cản",
     "Cây xanh, cành cây hoặc vật cản gây cản trở/nguy hiểm.", 5),
    ("TRAFFIC_SIGNS", "Biển báo",
     "Biển báo giao thông hư hỏng, mất, che khuất hoặc bất cập.", 6),
    ("TRAFFIC_ORGANIZATION", "Tổ chức giao thông",
     "Bất cập về phân luồng, phân làn và tổ chức lưu thông.", 7),
    ("TRAFFIC_LIGHTS", "Đèn tín hiệu",
     "Sự cố đèn tín hiệu giao thông hoặc chu kỳ tín hiệu.", 8),
    ("WASTE_ENVIRONMENT", "Rác thải/Vệ sinh môi trường",
     "Rác thải, vệ sinh công cộng và ô nhiễm môi trường đô thị.", 9),
    ("OBSTRUCTIVE_PARKING", "Đỗ xe cản trở",
     "Phương tiện dừng/đỗ gây cản trở giao thông hoặc lối đi.", 10),
    ("OTHER", "Khác",
     "Phản ánh hợp lệ không thuộc mười danh mục còn lại.", 11),
)


def seed_categories(session: Session) -> None:
    existing = {
        category.category_code: category
        for category in session.scalars(select(IncidentCategory)).all()
    }

    expected_codes = {item[0] for item in CATEGORIES}
    unexpected_codes = set(existing) - expected_codes
    if unexpected_codes:
        raise RuntimeError(
            "Unexpected incident category codes in database: "
            + ", ".join(sorted(unexpected_codes))
        )

    for code, name, description, sort_order in CATEGORIES:
        current = existing.get(code)
        if current is None:
            session.add(
                IncidentCategory(
                    category_code=code,
                    category_name=name,
                    description=description,
                    sort_order=sort_order,
                    is_active=True,
                )
            )
            continue

        if current.category_name != name or current.sort_order != sort_order:
            raise RuntimeError(
                f"Category catalog drift detected for {code}; "
                "do not rename/reorder labels with an ordinary seed."
            )

        if not current.is_active:
            raise RuntimeError(
                f"Baseline category {code} is inactive; explicit review required."
            )


def main() -> None:
    Base.metadata  # Import-time assertion that models have been registered.
    with Session(engine) as session, session.begin():
        seed_categories(session)

    print(f"Seeded/verified exactly {len(CATEGORIES)} ST-NLP categories.")


if __name__ == "__main__":
    main()
