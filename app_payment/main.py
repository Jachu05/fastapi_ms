import asyncio
import time
from typing import List

import httpx
from fastapi import FastAPI, Depends
from fastapi.background import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from starlette import status
from starlette.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)
import models
import schemas
from database import get_async_session, async_engine
from schemas import OrderBase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=["*"],
)


# run with --port=8001
@app.get("/")
def root():
    return {"Hello": "World payment"}


@app.get("/orders", status_code=status.HTTP_200_OK, response_model=List[schemas.OrderOut])
async def get_all_orders(async_db: AsyncSession = Depends(get_async_session)):
    query = select(models.Order)
    orders = await async_db.execute(query)
    return orders.scalars().all()


@app.post("/orders")
async def create(request: OrderBase, background_task: BackgroundTasks
                 ):
    async with httpx.AsyncClient() as client:
        response = await helper_create_order(request, client, background_task)
    return response


async def helper_create_order(request: OrderBase, client, background_task: BackgroundTasks,
                              ):
    product = await client.get(f"http://localhost:8000/products/{request.product_id}")
    product_in_scheme = schemas.ProductOut(**product.json())

    new_order = models.Order(product_id=product_in_scheme.id,
                             price=product_in_scheme.price,
                             fee=0.2 * product_in_scheme.price,
                             total=1.2 * product_in_scheme.price,
                             quantity=product_in_scheme.quantity,
                             status=models.Status.PENDING)

    async with AsyncSession(async_engine) as async_db:
        async_db.add(new_order)
        await async_db.commit()
        await async_db.refresh(new_order)
        background_task.add_task(order_completed, new_order.id)

    return new_order


@app.post("/orders/bulk")
async def create_bulk(request: schemas.ListOrders, background_task: BackgroundTasks
                      ):
    async with httpx.AsyncClient() as client:
        reqs_list = []
        for req in request.data:
            reqs_list.append(helper_create_order(req, client, background_task))
        result = await asyncio.gather(*reqs_list)

    return result


async def order_completed(order_id: models.Order.id):
    time.sleep(1)  # simulates calculation
    record = update(models.Order).where(models.Order.id == order_id)
    record = record.values(status=models.Status.COMPLETED)
    record.execution_options(synchronize_session="fetch")
    async with AsyncSession(async_engine) as async_db:
        await async_db.execute(record)
        await async_db.commit()
