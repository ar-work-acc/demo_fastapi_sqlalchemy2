"""
Pydantic models for FastAPI.
"""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer

from model.product import ProductType


class ProductBase(BaseModel):
    """
    Common base model for creating and reading data.
    """

    product_name: str = ""
    unit_price: Annotated[
        Decimal,
        # https://docs.pydantic.dev/latest/api/standard_library_types/#decimaldecimal
        PlainSerializer(
            lambda x: round(x, 2), return_type=Decimal, when_used="json"
        ),
    ] = Decimal(0)
    units_in_stock: int = 0
    type: ProductType = ProductType.OTHER


class ProductInput(ProductBase):
    """
    Input model for data creation, so you can avoid passing back specific
    attributes, such as a password or a temporary field that assists creation.
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
