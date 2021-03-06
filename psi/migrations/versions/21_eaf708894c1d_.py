""" Make email field not null in user

Revision ID: eaf708894c1d
Revises: b9a78540086e
Create Date: 2016-04-21 23:40:36.604735

"""

# revision identifiers, used by Alembic.
revision = 'eaf708894c1d'
down_revision = 'b9a78540086e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'email', existing_type=sa.VARCHAR(length=255), nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'email', existing_type=sa.VARCHAR(length=255), nullable=True)
    ### end Alembic commands ###
