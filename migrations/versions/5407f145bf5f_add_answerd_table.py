"""add answerd table

Revision ID: 5407f145bf5f
Revises: 2cf83e16b3b7
Create Date: 2016-06-16 21:54:29.307473

"""

# revision identifiers, used by Alembic.
revision = '5407f145bf5f'
down_revision = '2cf83e16b3b7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answerd',
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.Column('posts_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['posts_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('answerd')
    ### end Alembic commands ###
