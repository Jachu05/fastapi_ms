import enum

import sqlalchemy as sa

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)

    name = sa.Column(sa.String, nullable=False, unique=True)
    price = sa.Column(sa.Float, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))


class Status(str, enum.Enum):
    PENDING = enum.auto()
    COMPLETED = enum.auto()
    REFUNDED = enum.auto()


class Order(Base):
    __tablename__ = "orders"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)

    price = sa.Column(sa.Float, nullable=False)
    fee = sa.Column(sa.Float, nullable=False)
    total = sa.Column(sa.Float, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    status = sa.Column(sa.Enum(Status), nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))

    product_id = sa.Column(sa.Integer, sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
