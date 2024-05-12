from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model import Base

if TYPE_CHECKING:
    from model import Order, Product


class OrderDetail(Base):
    """
    Association object pattern.
    This uses the associative table between Order and Product.
    """
    __tablename__ = "order_detail"

    order_id: Mapped[int] = mapped_column(
        # database side: ON DELETE CASCADE
        ForeignKey("order.order_id", ondelete="CASCADE"),
        primary_key=True,
        default=None,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.product_id"),
        primary_key=True,
        default=None,
    )

    quantity: Mapped[int] = mapped_column(
        CheckConstraint(
            "quantity>0",
            name="num_of_ordered_item_must_be_positive",
        ),
        default=1,
    )

    order: Mapped[Order] = relationship(
        back_populates="order_details",
        init=False,
        repr=False,
    )

    product: Mapped[Product] = relationship(
        back_populates="order_details",
        init=False,
        repr=False,
    )
