from __future__ import annotations

from typing import TYPE_CHECKING  # PEP-563

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model import Base, date_auto, int_pk, str_127
from model.common import EmailValidatorMixin

if TYPE_CHECKING:
    from model import Order


class Employee(EmailValidatorMixin, Base):
    __tablename__ = "employee"

    employee_id: Mapped[int_pk] = mapped_column(init=False)

    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee.employee_id"),
        default=None,
    )

    email: Mapped[str_127] = mapped_column(
        CheckConstraint(
            "length(email)>5",
            name="email_length_min_length_constraint",
        ),
        unique=True,
        default="",
    )
    password_hash: Mapped[str] = mapped_column(
        default="",
    )
    first_name: Mapped[str_127] = mapped_column(
        CheckConstraint(
            "length(first_name)>0",
            name="name_length_must_be_at_least_one_character",
        ),
        default="",
    )
    last_name: Mapped[str_127 | None] = mapped_column(
        default="",
    )

    is_manager: Mapped[bool] = mapped_column(default=False)
    hire_date: Mapped[date_auto] = mapped_column(default=None)

    # self-referential relationship: manager/employees
    manager: Mapped[Employee] = relationship(
        back_populates="employees",
        remote_side=[employee_id],
        init=False,
        repr=False,
    )
    employees: Mapped[list[Employee]] = relationship(
        back_populates="manager",
        init=False,
        repr=False,
    )

    orders: Mapped[list[Order]] = relationship(
        back_populates="employee",
        init=False,
        repr=False,
    )
