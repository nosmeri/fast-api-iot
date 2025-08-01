"""empty message

Revision ID: d38fcad2f304
Revises: 745565c2ec9e
Create Date: 2025-08-02 03:51:59.394145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd38fcad2f304'
down_revision: Union[str, Sequence[str], None] = '745565c2ec9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TYPE userrole")
    op.create_enum("userrole", ["ADMIN", "MANAGER", "MEMBER"])

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
