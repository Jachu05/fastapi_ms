import asyncio
import time
from typing import List

import httpx
import requests
from fastapi import FastAPI, Depends
from fastapi.background import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)
import models
import schemas
from database import get_async_session
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


# async run
# @app.post("/orders")
# async def create(request: Request):
#     body = await request.json()
#     print(body)
#
#     async with httpx.AsyncClient() as client:
#         req = []
#         for _ in range(5):
#             req.append(client.get(f"http://localhost:8000/products/{body['id']}"))
#         result = await asyncio.gather(*req)
#         pprint(list(map(lambda x: x.text, result)))


@app.post("/orders")
async def create(request: OrderBase, background_task: BackgroundTasks,
                 async_db: AsyncSession = Depends(get_async_session)):
    product = requests.get(f"http://localhost:8000/products/{request.product_id}")
    product_in_scheme = schemas.ProductOut(**product.json())

    new_order = models.Order(product_id=product_in_scheme.id,
                             price=product_in_scheme.price,
                             fee=0.2 * product_in_scheme.price,
                             total=1.2 * product_in_scheme.price,
                             quantity=product_in_scheme.quantity,
                             status=models.Status.PENDING)
    async_db.add(new_order)
    await async_db.commit()

    await async_db.refresh(new_order)

    background_task.add_task(order_completed, new_order, async_db)

    return new_order


@app.post("/orders/bulk")
async def create_bulk(request: schemas.ListOrders, background_task: BackgroundTasks,
                      async_db: AsyncSession = Depends(get_async_session)):

    async with httpx.AsyncClient() as client:
        reqs_list = []
        for req in request.data:
            reqs_list.append(client.get(f"http://localhost:8000/products/{req.product_id}"))
        result = await asyncio.gather(*reqs_list)
        # pprint(list(map(lambda x: x.text, result)))


def order_completed(order: models.Order, async_db: AsyncSession):
    time.sleep(10)
    order.status = models.Status.COMPLETED
    async_db.commit()
