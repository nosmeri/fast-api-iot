"""empty message

Revision ID: 745565c2ec9e
Revises: f26fb2fbd3e9
Create Date: 2025-08-02 03:46:21.450813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '745565c2ec9e'
down_revision: Union[str, Sequence[str], None] = 'f26fb2fbd3e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_enum("userrole", ["admin", "user", "guest"])
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("ADMIN", "MANAGER", "MEMBER", name="userrole"),
            nullable=False,
        ),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
