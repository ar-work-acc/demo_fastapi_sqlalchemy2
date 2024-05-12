from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model import Base, int_pk, timestamp_auto

if TYPE_CHECKING:
    from model import Customer, Employee, OrderDetail, Product


class Order(Base):
    __tablename__ = "order"

    order_id: Mapped[int_pk] = mapped_column(init=False)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.customer_id"),
        default=None,
    )
    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employee.employee_id"),
        default=None,
    )

    order_datetime: Mapped[timestamp_auto] = mapped_column(init=False)
    is_shipped: Mapped[bool] = mapped_column(default=False)

    customer: Mapped[Customer] = relationship(
        back_populates="orders",
        init=False,
        repr=False,
    )
    employee: Mapped[Employee | None] = relationship(
        back_populates="orders",
        init=False,
        repr=False,
    )

    # relationship with associative table:
    order_details: Mapped[list[OrderDetail]] = relationship(
        back_populates="order",
        init=False,
        repr=False,
        # cascade: "all" implies "refresh-expire", avoid using it with asyncio
        cascade="save-update, merge, expunge, delete, delete-orphan",
        passive_deletes=True,
    )

    # many-to-many relationship with `Product`, bypassing `OrderDetail` class
    products: Mapped[list[Product]] = relationship(
        init=False,
        repr=False,
        secondary="order_detail",
        back_populates="orders",
        viewonly=True,  # avoid conflicting changes between relations
    )

    product_names: AssociationProxy[list[str]] = association_proxy(
        "products",
        "product_name",
        init=False,
        repr=False,
    )
