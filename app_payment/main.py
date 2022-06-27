import time
from typing import List

import requests
from fastapi import FastAPI, Depends
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session
from starlette import status
from starlette.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)
import models
import schemas
from database import get_db
from schemas import OrderBase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"Hello": "World payment"}


@app.get("/orders", status_code=status.HTTP_200_OK, response_model=List[schemas.OrderOut])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    return orders

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
async def create(request: OrderBase, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    product = requests.get(f"http://localhost:8000/products/{request.product_id}")
    product_in_scheme = schemas.ProductOut(**product.json())

    new_order = models.Order(product_id=product_in_scheme.id,
                             price=product_in_scheme.price,
                             fee=0.2 * product_in_scheme.price,
                             total=1.2 * product_in_scheme.price,
                             quantity=product_in_scheme.quantity,
                             status=models.Status.PENDING)
    db.add(new_order)
    db.commit()

    db.refresh(new_order)

    background_task.add_task(order_completed, new_order, db)

    return new_order


def order_completed(order: models.Order, db: Session):
    time.sleep(10)
    order.status = models.Status.COMPLETED
    db.commit()

