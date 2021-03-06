"""add_created_at_to_products

Revision ID: f8480d9122ff
Revises: a6d1ddac050c
Create Date: 2022-06-26 16:56:24.509869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8480d9122ff'
down_revision = 'a6d1ddac050c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.create_unique_constraint(None, 'products', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'products', type_='unique')
    op.drop_column('products', 'created_at')
    # ### end Alembic commands ###
