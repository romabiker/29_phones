from alembic import op
import sqlalchemy as sa


revision = 'b6d4be229078'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('orders', sa.Column(
            'normalized_phones',
            sa.Numeric(precision=15), nullable=True)
        )


def downgrade():
    op.alter_column(table_name='orders', column_name='normalized_phones')
