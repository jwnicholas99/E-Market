"""Added image field to product model

Revision ID: 5cfe313a2f3b
Revises: e1839be1c92d
Create Date: 2019-06-17 23:50:28.644403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cfe313a2f3b'
down_revision = 'e1839be1c92d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('image_url', sa.String(length=400), nullable=True))
    op.create_index(op.f('ix_product_image_url'), 'product', ['image_url'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_product_image_url'), table_name='product')
    op.drop_column('product', 'image_url')
    # ### end Alembic commands ###