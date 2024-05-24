import logging
from decimal import Decimal
from test.conftest import PRODUCT_DATA
from test.integration import (
    NON_EXISTING_PRODUCT_ID,
    UNAUTHORIZED_RESPONSE,
    is_valid_uuid,
)

from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from model import ProductType
from repository import product as product_repo
from schema.product import ProductCreate

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

    product_json = response.json()["product"]
    # note: CamelCase
    assert product_json["product_name"] == "Test Phone"
    # note: scale is 2 (set in Pydantic)
    assert product_json["unit_price"] == "100.00"
    assert product_json["units_in_stock"] == 5
    assert product_json["type"] == ProductType.PHONE.value
    assert "product_id" in product_json

    assert is_valid_uuid(response.json()["task_id"])


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


async def test_user_get_non_existing_product_detail(
    async_client: AsyncClient,
    auth_header_user: dict[str, str],
) -> None:
    product_id = NON_EXISTING_PRODUCT_ID
    response = await async_client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_header_user,
    )

    assert response.status_code == 404

    json_response = response.json()
    assert json_response["detail"] == f"Product #{product_id} not found!"


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
    assert response.json() == UNAUTHORIZED_RESPONSE


async def test_get_product_pages(
    async_client: AsyncClient,
) -> None:

    async def get_page(page_number: int = 1) -> Response:
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


async def test_admin_delete_product(
    session: AsyncSession,
    async_client: AsyncClient,
    auth_header_admin: dict[str, str],
) -> None:
    product = await product_repo.create_product(
        session,
        ProductCreate(
            product_name="test product",
            unit_price=Decimal(1),
        ),
    )
    assert product is not None

    product_id = product.product_id
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_header_admin,
    )
    assert response.status_code == 204


async def test_admin_delete_non_existing_product(
    async_client: AsyncClient,
    auth_header_admin: dict[str, str],
) -> None:
    product_id = NON_EXISTING_PRODUCT_ID
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_header_admin,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Product #{product_id} not found! Cannot delete product."
    }


async def test_user_delete_product_failure(
    async_client: AsyncClient,
    auth_header_user: dict[str, str],
) -> None:
    product_id = 1
    response = await async_client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_header_user,
    )
    assert response.status_code == 403
    assert response.json() == UNAUTHORIZED_RESPONSE


async def test_admin_update_product(
    session: AsyncSession,
    async_client: AsyncClient,
    auth_header_admin: dict[str, str],
) -> None:
    # create a product for update
    product = await product_repo.create_product(
        session,
        ProductCreate(
            product_name="test product",
            unit_price=Decimal(1),
        ),
    )
    assert product is not None

    # next, update this product with the following
    product_id = product.product_id
    data = {
        "product_name": "test update",
        "unit_price": 999,
        "units_in_stock": 999,
        "type": ProductType.PHONE.value,
    }
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        headers=auth_header_admin,
        json=data,
    )

    assert response.status_code == 200

    json_result = response.json()
    assert json_result["product_id"] == product_id
    assert json_result["product_name"] == "Test Update"  # CamelCase
    assert json_result["unit_price"] == "999.00"  # scale: 2 (Pandoc)
    assert json_result["units_in_stock"] == 999
    assert json_result["type"] == ProductType.PHONE.value


async def test_admin_update_product_units_in_stock(
    session: AsyncSession,
    async_client: AsyncClient,
    auth_header_admin: dict[str, str],
) -> None:
    # create a product for update
    product = await product_repo.create_product(
        session,
        ProductCreate(
            product_name="test phone",
            unit_price=Decimal(100),
            type=ProductType.PHONE,
        ),
    )
    assert product is not None

    # next, update this product's units in stock
    product_id = product.product_id
    data = {
        "units_in_stock": 20,
    }
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        headers=auth_header_admin,
        json=data,
    )

    assert response.status_code == 200

    json_result = response.json()
    assert json_result["product_id"] == product_id
    assert json_result["product_name"] == "Test Phone"  # CamelCase
    assert json_result["unit_price"] == "100.00"  # scale: 2
    assert json_result["units_in_stock"] == 20
    assert json_result["type"] == ProductType.PHONE.value


async def test_admin_update_non_existing_product(
    async_client: AsyncClient,
    auth_header_admin: dict[str, str],
) -> None:
    product_id = NON_EXISTING_PRODUCT_ID
    data = {
        "product_name": "test update",
        "unit_price": 999,
        "units_in_stock": 999,
        "type": ProductType.PHONE.value,
    }
    response = await async_client.put(
        f"/api/v1/products/{product_id}",
        headers=auth_header_admin,
        json=data,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Product #{product_id} not found! Aborting the update."
    }
