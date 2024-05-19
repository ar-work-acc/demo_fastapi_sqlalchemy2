from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from model.product import ProductType
from schema.product import ProductCreate
from service.product import create_product


async def test_get_product(session: AsyncSession) -> None:
    input_product = ProductCreate(
        product_name="test other",
        unit_price=Decimal(100),
    )
    product = await create_product(session, input_product)
    assert product.product_id is not None
    assert product.product_name == "Test Other"  # CamelCase
    assert product.unit_price == input_product.unit_price
    assert product.units_in_stock == 0
    assert product.type == ProductType.OTHER
