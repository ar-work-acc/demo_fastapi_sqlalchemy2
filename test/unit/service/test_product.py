from model.product import ProductType
from schema.product import ProductInput
from service.product import create_product


async def test_get_product(session):
    input_product = ProductInput(
        product_name="test other",
        unit_price=100,
    )
    product = await create_product(session, input_product)
    assert product.product_id is not None
    assert product.product_name == "Test Other"  # CamelCase
    assert product.unit_price == input_product.unit_price
    assert product.units_in_stock == 0
    assert product.type == ProductType.OTHER
