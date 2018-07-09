"""empty message

Revision ID: a08c669eb20c
Revises: 
Create Date: 2018-07-07 12:33:55.368687

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a08c669eb20c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'status')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('status', mysql.SMALLINT(display_width=6), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
