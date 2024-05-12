import logging
from test.conftest import PRODUCT_DATA

from httpx import AsyncClient

from model import ProductType

logger = logging.getLogger(__name__)


async def test_admin_create_product(
    async_client: AsyncClient,
    auth_header_admin: dict[str, str],
) -> None:
    data = {
        "product_name": "test phone",
        "unit_price": 100.0,
        "units_in_stock": 5,
        "type": ProductType.PHONE.value,
    }
    response = await async_client.post(
        "/api/v1/products/",
        headers=auth_header_admin,
        json=data,
    )
    assert response.status_code == 201

    json_result = response.json()
    # note: CamelCase
    assert json_result["product_name"] == "Test Phone"
    # note: scale is 2 (set in Pydantic)
    assert json_result["unit_price"] == "100.00"
    assert json_result["units_in_stock"] == 5
    assert json_result["type"] == ProductType.PHONE.value
    assert "product_id" in json_result


async def test_user_get_product_detail(
    async_client: AsyncClient,
    auth_header_user: dict[str, str],
) -> None:
    # set a product ID between 1-5
    product_id = 1

    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_header_user,
    )

    assert response.status_code == 200

    x = PRODUCT_DATA[product_id - 1]
    x["product_id"] = product_id
    x["product_name"] = str(x["product_name"]).title()
    x["unit_price"] = "{:.2f}".format(float(str(x["unit_price"])))
    assert response.json() == x


async def test_user_create_product_failure(
    async_client: AsyncClient,
    auth_header_user: dict[str, str],
) -> None:
    data = {
        "product_name": "test user product",
        "unit_price": 100.0,
        "units_in_stock": 5,
        "type": ProductType.PHONE.value,
    }

    response = await async_client.post(
        "/api/v1/products/",
        headers=auth_header_user,
        json=data,
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Unauthorized. Only managers can access this endpoint."
    }


async def test_get_product_pages(
    async_client: AsyncClient,
) -> None:

    async def get_page(page_number: int = 1):
        params = {
            "page": str(page_number),
            "page_size": str(2),
            "order_by": "product_id",
            "direction": "desc",
        }
        response = await async_client.get(
            "/api/v1/products/",
            params=params,
        )
        return response

    response = await get_page(1)
    assert response.status_code == 200
    json_result = response.json()
    assert len(json_result) == 2  # page size
    product_id_11 = json_result[0]["product_id"]
    product_id_12 = json_result[1]["product_id"]

    response = await get_page(2)
    assert response.status_code == 200
    json_result = response.json()
    assert len(json_result) == 2
    product_id_21 = json_result[0]["product_id"]
    product_id_22 = json_result[1]["product_id"]

    # page, order_by, direction
    assert product_id_11 > product_id_12 > product_id_21 > product_id_22
