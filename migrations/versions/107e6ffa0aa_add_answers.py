"""ADD answers

Revision ID: 107e6ffa0aa
Revises: 2ba0275a651
Create Date: 2016-04-11 22:07:58.797566

"""

# revision identifiers, used by Alembic.
revision = '107e6ffa0aa'
down_revision = '2ba0275a651'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('agree', sa.Integer(), nullable=True),
    sa.Column('disagree', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_answers_timestamp', 'answers', ['timestamp'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_answers_timestamp', 'answers')
    op.drop_table('answers')
    ### end Alembic commands ###
