"""
Pydantic models for FastAPI.
"""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer

from model.product import ProductType


class ProductBase(BaseModel):
    """
    Common base model.
    """

    product_name: str | None = None
    unit_price: Decimal | None = None
    units_in_stock: int | None = None
    type: ProductType | None = None


class ProductCreate(ProductBase):
    """
    For product creation.
    """

    product_name: str  # required field
    unit_price: Decimal = Decimal(0)
    units_in_stock: int = 0
    type: ProductType = ProductType.OTHER


class ProductUpdate(ProductBase):
    """
    For partial updates; all fields are optional.
    """

    pass


class ProductOutput(ProductBase):
    """
    Use this output model to include additional fields you want to return to
    the user, including fields that are generated after model creation
    (e.g, ID), or fields that are calculated, such as relationship fields.
    """

    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    unit_price: Annotated[
        Decimal,
        # https://docs.pydantic.dev/latest/api/standard_library_types/#decimaldecimal
        PlainSerializer(
            lambda x: round(x, 2), return_type=Decimal, when_used="json"
        ),
    ]
    units_in_stock: int
    type: ProductType
