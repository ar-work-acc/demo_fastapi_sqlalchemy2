import enum
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column
from model import Base, uuid_pk


class NotificationType(enum.Enum):
    PRODUCT = 0
    OTHER = 1


class SystemEmail(Base):
    __tablename__ = "system_email"

    # Celery task UUID as PK (chance of collision is low)
    task_id: Mapped[uuid_pk] = mapped_column(Uuid)

    target_id: Mapped[int]
    type: Mapped[NotificationType] = mapped_column(
        default=NotificationType.OTHER,
    )
    is_sent: Mapped[bool] = mapped_column(default=False)
