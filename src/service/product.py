"""
Database CRUD operations for FastAPI service.
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

import repository.product as product_repo
from schema.product import ProductInput

logger = logging.getLogger(__name__)


async def create_product(
    session: AsyncSession,
    product: ProductInput,
):
    db_product = await product_repo.create_product(session, product)

    # test: try and comment out `expire_on_commit=False`
    logger.debug(f"Product created: {db_product.product_id}")

    return db_product


async def get_product(
    session: AsyncSession,
    product_id: int,
):
    product = await product_repo.get_product(session, product_id)

    if product is not None:
        # test: load relationship (lazy loading in async)
        orders = await product.awaitable_attrs.orders
        logger.debug(f"Orders should be empty: {orders}")

        # you can NOT directly access orders
        # without explicitly loading it first
        # (try and comment out the above)
        logger.debug(f"product.orders: {product.orders}")

    return product


async def get_products(
    session: AsyncSession,
    page: int,
    page_size: int,
    order_by: str,
    direction: str,
):
    return await product_repo.get_products(
        session,
        page,
        page_size,
        order_by,
        direction,
    )
