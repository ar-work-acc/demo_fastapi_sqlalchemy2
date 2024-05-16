from fastapi import APIRouter, Depends

import service.product as product_service
from core.dependency import (AsyncSessionDep, check_logged_in_user_is_manager,
                             oauth2_scheme)
from model.product import Product
from schema.product import ProductInput, ProductOutput

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    response_model=ProductOutput,
    dependencies=[Depends(check_logged_in_user_is_manager)],
)
async def create_product(
    product: ProductInput,
    session: AsyncSessionDep,
) -> Product:
    """An endpoint to create products. Only managers can access this endpoint.

    Args:
        product (ProductInput): The product input model.
        session (Annotated[AsyncSession, Depends): The injected session object.

    Returns:
        ProductOutput: The Pydantic output model of the product just created.
    """
    return await product_service.create_product(session, product)


@router.get(
    "/{product_id}",
    response_model=ProductOutput,
    dependencies=[Depends(oauth2_scheme)],
)
async def get_product(
    product_id: int,
    session: AsyncSessionDep,
) -> Product:
    """Get the product detail of a product by its id.
    Only logged in users can access this endpoint.

    Args:
        product_id (int): The product ID (primary key).
        session (AsyncSession, optional): The injected session object.

    Returns:
        ProductOutput: The output model of the target product.
    """
    return await product_service.get_product(session, product_id)


@router.get("/", response_model=list[ProductOutput])
async def get_products(
    session: AsyncSessionDep,
    page: int = 1,
    page_size: int = 3,
    order_by: str = "product_id",
    direction: str = "asc",
) -> list[Product]:
    """Get a page of products (pagination).

    Args:
        page (int, optional): The page number. Defaults to 1.
        page_size (int, optional): The size of each page. Defaults to 3.
        order_by (str, optional): The column to sort by.
        Defaults to "product_id".
        direction (str, optional): The direction of the sort.
        Defaults to "asc".
        session (AsyncSession, optional): The injected session object.

    Returns:
        list[ProductOutput]: The list of products in the requested page.
    """
    return await product_service.get_products(
        session,
        page,
        page_size,
        order_by,
        direction,
    )


@router.put(
    "/{product_id}",
    dependencies=[Depends(check_logged_in_user_is_manager)],
    response_model=ProductOutput,
)
async def update_product(
    session: AsyncSessionDep,
    product_id: int,
    product_data: ProductInput,
) -> Product:
    """An endpoint to update products. Only managers can access this endpoint.

    Args:
        session (AsyncSessionDep): Injected async session object.
        product_id (int): product primary key
        product_data (ProductInput): The product input model (fields to update)

    Returns:
        _type_: _description_
    """
    product = await product_service.update_product(
        session, product_id, product_data
    )

    return product


@router.delete(
    "/{product_id}",
    status_code=204,
    dependencies=[Depends(check_logged_in_user_is_manager)],
)
async def delete_product(
    session: AsyncSessionDep,
    product_id: int,
) -> None:
    """An endpoint to delete products. Only managers can access this endpoint.

    Args:
        session (AsyncSessionDep): DI injected async session object.
        product_id (int): The product's primary key.
    """
    await product_service.delete_product(session, product_id)
