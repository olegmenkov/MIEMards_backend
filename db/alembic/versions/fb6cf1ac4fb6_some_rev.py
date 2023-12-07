"""some rev

Revision ID: fb6cf1ac4fb6
Revises: 80211fa6c2a8
Create Date: 2023-12-07 10:06:39.520437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb6cf1ac4fb6'
down_revision: Union[str, None] = '80211fa6c2a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
