"""change password field name

Revision ID: 7ba234818bf3
Revises: 569749a64c19
Create Date: 2025-07-19 05:26:01.270045

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "7ba234818bf3"
down_revision: Union[str, Sequence[str], None] = "569749a64c19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column(
            "hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
    )
    op.drop_column("user", "password")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user", sa.Column("password", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.drop_column("user", "hashed_password")
    # ### end Alembic commands ###
