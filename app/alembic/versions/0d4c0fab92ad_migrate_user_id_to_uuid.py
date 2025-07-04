"""migrate user id to uuid

Revision ID: 0d4c0fab92ad
Revises: 21eee5081d8a
Create Date: 2025-07-04 23:02:46.072474

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = "0d4c0fab92ad"
down_revision: Union[str, Sequence[str], None] = "21eee5081d8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 새 UUID 컬럼 추가
    op.add_column("users", sa.Column("id_new", sa.String(), nullable=True))

    # 2. UUID 값으로 채우기
    conn = op.get_bind()
    results = conn.execute(sa.text("SELECT id FROM users")).fetchall()
    for row in results:
        conn.execute(
            sa.text("UPDATE users SET id_new = :uuid WHERE id = :id"),
            {"uuid": str(uuid.uuid4()), "id": row.id},
        )

    # 3. PK 교체
    op.drop_constraint("users_pkey", "users", type_="primary")
    op.drop_column("users", "id")
    op.alter_column("users", "id_new", new_column_name="id")
    op.create_primary_key("users_pkey", "users", ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    pass
