from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '04b37dfb6263'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('orders', sa.Column('normalized_phone', sa.Numeric(precision=15, scale=0), nullable=True))


def downgrade():
    op.drop_column('orders', 'normalized_phone')
