from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.product import Product
from schema.product import ProductInput


async def create_product(
    session: AsyncSession, product: ProductInput
) -> Product:
    db_product = Product(**product.model_dump())
    session.add(db_product)
    await session.commit()

    return db_product


async def get_product(
    session: AsyncSession, product_id: int
) -> Product | None:
    return await session.get(Product, product_id)


async def get_products(
    session: AsyncSession,
    page: int,
    page_size: int,
    order_by: str,
    direction: str,
) -> Sequence[Product]:
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


async def update_product(
    session: AsyncSession,
    product_id: int,
    product_data: ProductInput,
) -> Product:
    # check if the model exists in the database
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product #{product_id} not found! Aborting the update.",
        )

    # if it does, update its attributes with values from the Pandoc model
    for key, value in product_data.model_dump().items():
        setattr(product, key, value)
    await session.commit()

    return product


async def delete_product(
    session: AsyncSession,
    product_id: int,
) -> None:
    product = await session.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product #{product_id} not found! Cannot delete product.",
        )

    await session.delete(product)
    await session.commit()
