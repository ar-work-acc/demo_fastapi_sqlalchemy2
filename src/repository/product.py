from fastapi import HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from model import Product
from schema.product import ProductInput


async def create_product(session: AsyncSession, product: ProductInput):
    db_product = Product(**product.model_dump())
    session.add(db_product)
    await session.commit()

    return db_product


async def get_product(session: AsyncSession, product_id: int):
    return await session.get(Product, product_id)


async def get_products(
    session: AsyncSession,
    page: int,
    page_size: int,
    order_by: str,
    direction: str,
):
    stmt = select(Product).offset((page - 1) * page_size).limit(page_size)

    if direction == "asc":
        stmt = stmt.order_by(order_by)
    elif direction == "desc":
        stmt = stmt.order_by(desc(order_by))
    else:
        raise HTTPException(
            status_code=400,
            detail="Use asc or desc for the direction parameter.",
        )

    products = (await session.scalars(stmt)).all()

    return products
