from decimal import Decimal
from model import Product


def test_product_repr() -> None:
    product = Product(
        product_name="test",
        unit_price=Decimal(1.00),
    )

    assert str(product) == (
        "Product(product_id=None, product_name='Test', "
        "unit_price=1, units_in_stock=0, type='other')"
    )
