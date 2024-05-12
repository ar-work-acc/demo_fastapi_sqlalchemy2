from __future__ import annotations  # PEP-563

from typing import TYPE_CHECKING

from sqlalchemy import Index
from sqlalchemy.orm import (Mapped, mapped_column, query_expression,
                            relationship)

from model import Base, int_pk, str_127, str_255
from model.common import EmailValidatorMixin

if TYPE_CHECKING:
    from model import Order


class Customer(EmailValidatorMixin, Base):
    __tablename__ = "customer"

    customer_id: Mapped[int_pk] = mapped_column(init=False)

    first_name: Mapped[str_127]
    last_name: Mapped[str_127]
    # deferred attributes needs to be loaded eagerly in async
    address: Mapped[str_255] = mapped_column(
        deferred=True,
        deferred_group="customer_attributes",
    )
    email: Mapped[str_127] = mapped_column(unique=True)

    order_count: Mapped[int] = query_expression(repr=False)

    __table_args__ = (Index("customer_full_name", "first_name", "last_name"),)

    # same with lazily loaded relationships, you can use:
    # `await customer.awaitable_attrs.orders`
    orders: Mapped[list[Order]] = relationship(
        lazy="select",
        back_populates="customer",
        init=False,
        repr=False,
        order_by="desc(Order.order_id)",
    )
