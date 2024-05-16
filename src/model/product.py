from __future__ import annotations  # PEP-563

import enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from model import Base, int_pk, num_12_2, str_255

if TYPE_CHECKING:
    from model import Order, OrderDetail


class ProductType(enum.Enum):
    """
    The enumeration for our product types.
    Products are divided into: phone, accessory, and other types.
    """

    PHONE = 0
    ACCESSORY = 1
    OTHER = 2


class Product(Base, repr=False):  # type: ignore
    __tablename__ = "product"

    product_id: Mapped[int_pk] = mapped_column(init=False)

    product_name: Mapped[str_255] = mapped_column(index=True)
    unit_price: Mapped[num_12_2] = mapped_column(
        CheckConstraint("unit_price>0")
    )
    units_in_stock: Mapped[int] = mapped_column(
        CheckConstraint("units_in_stock>=0"),
        default=0,
    )
    type: Mapped[ProductType] = mapped_column(
        default=ProductType.OTHER,
    )

    order_details: Mapped[list[OrderDetail]] = relationship(
        init=False,
        repr=False,
        back_populates="product",
    )

    # many-to-many relationship to `Order`, bypassing `OrderDetail`
    orders: Mapped[list[Order]] = relationship(
        init=False,
        secondary="order_detail",
        back_populates="products",
        viewonly=True,
    )

    # customize repr:
    def __repr__(self) -> str:
        return (
            "Product("
            f"product_id={self.product_id}, "
            f"product_name='{self.product_name}', "
            f"unit_price={self.unit_price}, "
            f"units_in_stock={self.units_in_stock}, "
            f"type='{self.type.name.lower()}'"
            ")"
        )

    @validates("product_name")
    def validate_product_name(self, key: Any, value: str) -> str:
        return value.title()
