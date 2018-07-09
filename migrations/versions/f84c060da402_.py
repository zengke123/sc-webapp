"""empty message

Revision ID: f84c060da402
Revises: a08c669eb20c
Create Date: 2018-07-09 13:34:27.021550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f84c060da402'
down_revision = 'a08c669eb20c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('host',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type', sa.String(length=32), nullable=False),
    sa.Column('cluster', sa.String(length=32), nullable=False),
    sa.Column('hostname', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hostname')
    )
    op.create_index(op.f('ix_host_cluster'), 'host', ['cluster'], unique=False)
    op.create_index(op.f('ix_host_type'), 'host', ['type'], unique=False)
    op.add_column('user', sa.Column('status', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'status')
    op.drop_index(op.f('ix_host_type'), table_name='host')
    op.drop_index(op.f('ix_host_cluster'), table_name='host')
    op.drop_table('host')
    # ### end Alembic commands ###
