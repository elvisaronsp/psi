""" Change remark in expense to required

Revision ID: 5590114aa058
Revises: 2673ce30fb12
Create Date: 2015-07-25 14:10:47.090629

"""

# revision identifiers, used by Alembic.
revision = '5590114aa058'
down_revision = '2673ce30fb12'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.execute("UPDATE expense SET remark = '' WHERE remark is NULL")
    op.alter_column('expense', 'remark', existing_type=sa.TEXT(), nullable=False,)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('expense', 'remark', existing_type=sa.TEXT(), nullable=True)
    ### end Alembic commands ###
