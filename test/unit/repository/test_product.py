from fastapi import HTTPException
import pytest
from repository.product import get_products


async def test_get_products_with_wrong_direction(session):
    with pytest.raises(HTTPException) as excinfo:
        await get_products(
            session,
            1,
            1,
            "product_id",
            direction="wrong_direction",
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == (
        'Use asc or desc '
        'for the direction parameter.'
    )


async def test_get_products_asc(session):
    products = await get_products(
        session,
        page=1,
        page_size=2,
        order_by="product_id",
        direction="asc",
    )

    assert products[0].product_id == 1
    assert products[1].product_id == 2
