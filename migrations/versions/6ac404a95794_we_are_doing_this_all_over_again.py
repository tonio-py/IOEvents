"""We are doing this all over again

Revision ID: 6ac404a95794
Revises: d6a31baf2dbd
Create Date: 2023-06-18 22:38:50.847462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ac404a95794'
down_revision = 'd6a31baf2dbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=400), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organizer', schema=None) as batch_op:
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###
