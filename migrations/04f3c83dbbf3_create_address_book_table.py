from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'address_book',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('address', sa.String(50)),
        sa.Column('phone', sa.String(15))
    )

def downgrade():
    op.drop_table('address_book')