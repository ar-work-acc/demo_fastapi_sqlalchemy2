"""
Database CRUD operations for FastAPI service.
"""

import logging
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import repository.product as product_repo
from model.product import Product
from schema.product import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


async def create_product(
    session: AsyncSession,
    product: ProductCreate,
) -> Product:
    db_product = await product_repo.create_product(session, product)

    # test: try and comment out `expire_on_commit=False`
    logger.debug(f"Product created: {db_product.product_id}")

    return db_product


async def get_product(
    session: AsyncSession,
    product_id: int,
) -> Product:
    product = await product_repo.get_product(session, product_id)

    if product is not None:
        # test: load relationship (lazy loading in async)
        orders = await product.awaitable_attrs.orders
        logger.debug(f"Orders should be empty: {orders}")

        # you can NOT directly access orders
        # without explicitly loading it first
        # (try and comment out the above)
        logger.debug(f"product.orders: {product.orders}")
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Product #{product_id} not found!",
        )

    return product


async def get_products(
    session: AsyncSession,
    page: int,
    page_size: int,
    order_by: str,
    direction: str,
) -> Sequence[Product]:
    return await product_repo.get_products(
        session,
        page,
        page_size,
        order_by,
        direction,
    )


async def update_product(
    session: AsyncSession,
    product_id: int,
    product_data: ProductUpdate,
) -> Product:
    return await product_repo.update_product(
        session,
        product_id,
        product_data,
    )


async def delete_product(
    session: AsyncSession,
    product_id: int,
) -> None:
    await product_repo.delete_product(session, product_id)
