"""ensure_admin_user

Revision ID: 883295019f6c
Revises: fd1419eac0ea
Create Date: 2025-08-23 21:20:09.902204

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.exc import IntegrityError

from dundie_api.models.user import User
from dundie_api.security import get_password_hash
from sqlmodel import Session

# revision identifiers, used by Alembic.
revision: str = "883295019f6c"
down_revision: Union[str, Sequence[str], None] = "fd1419eac0ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Coletando a conexão com o banco de dados usada pelo alembic.
    bind = op.get_bind()
    # Definindo uma sessão de banco de dados com a conexão do alembic.
    session = Session(bind=bind)

    # Criando um usuário admin a ser populado automaticamente.
    admin = User(
        name="Admin",
        username="admin",
        email="admin@dm.com",
        dept="management",
        currency="USD",
        password=get_password_hash("admin"),
    )

    # Tenta adicionar o usuário no banco de dados, caso ele já existir
    # ou então gerar algum, realiza o rollback dos comandos executados.
    try:
        session.add(admin)
        session.commit()
    except IntegrityError:
        session.rollback()


def downgrade() -> None:
    """Downgrade schema."""
    pass
