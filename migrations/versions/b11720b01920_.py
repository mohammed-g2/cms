"""empty message

Revision ID: b11720b01920
Revises: 6af496bfefbd
Create Date: 2020-05-23 21:07:23.415806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b11720b01920'
down_revision = '6af496bfefbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('default', sa.Boolean(), nullable=True))
    op.add_column('role', sa.Column('permissions', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_role_default'), 'role', ['default'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_role_default'), table_name='role')
    op.drop_column('role', 'permissions')
    op.drop_column('role', 'default')
    # ### end Alembic commands ###
