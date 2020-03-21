"""empty message

Revision ID: e9e3e115d850
Revises: 
Create Date: 2020-03-19 19:46:37.920294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9e3e115d850'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_info',
    sa.Column('file_ID', sa.Integer(), nullable=False),
    sa.Column('course_code', sa.String(length=10), nullable=False),
    sa.Column('course_name', sa.String(length=200), nullable=False),
    sa.Column('prof_name', sa.String(length=200), nullable=False),
    sa.Column('course_term', sa.String(length=20), nullable=False),
    sa.Column('file_name', sa.String(length=200), nullable=False),
    sa.Column('rating_avg', sa.Float(), nullable=False),
    sa.Column('file_path', sa.String(length=200), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('file_ID')
    )
    op.create_table('review_info',
    sa.Column('review_ID', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=False),
    sa.Column('review', sa.String(length=2048), nullable=False),
    sa.Column('review_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('review_ID')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review_info')
    op.drop_table('file_info')
    # ### end Alembic commands ###