from typing import List

from fastapi import FastAPI, Depends, status, HTTPException, Response
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

import models
import schemas
from database import get_async_session
from exceptions import DuplicatedEntryError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"Hello": "World inventory"}


@app.get("/products", status_code=status.HTTP_200_OK, response_model=List[schemas.ProductOut])
async def get_all_products(async_db: AsyncSession = Depends(get_async_session)):
    query = select(models.Product)
    products = await async_db.execute(query)
    return products.scalars().all()


@app.get("/products/{idx}", status_code=status.HTTP_200_OK, response_model=schemas.ProductOut)
async def get_product(idx: int, async_db: AsyncSession = Depends(get_async_session)):
    query = select(models.Product).filter(models.Product.id == idx)
    product = await async_db.execute(query)
    return product.scalars().first()


@app.post("/products", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductOut)
async def create_product(product: schemas.ProductBase, async_db: AsyncSession = Depends(get_async_session)):
    new_product = models.Product(**product.dict())
    async_db.add(new_product)

    try:
        await async_db.commit()
    except IntegrityError:
        await async_db.rollback()
        raise DuplicatedEntryError("The product is already stored")

    await async_db.refresh(new_product)
    return new_product


@app.delete("/products/{idx}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(idx: int, async_db: AsyncSession = Depends(get_async_session)):
    query = select(models.Product).filter(models.Product.id == idx)
    raw_product = await async_db.execute(query)
    product = raw_product.scalars().first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {idx} was not found')

    await async_db.delete(product)
    await async_db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/products/{idx}", response_model=schemas.ProductOut)
async def update_product(idx: int, product: schemas.ProductUpdate, async_db: AsyncSession = Depends(get_async_session)):
    up_product = models.Product(**product.dict())

    query = update(models.Product).where(models.Product.id == idx)
    query = query.values(name=up_product.name)
    query.execution_options(synchronize_session="fetch")
    await async_db.execute(query)
    return await async_db.commit()

