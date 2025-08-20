from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, Column, DateTime

# Realiza o import apenas no momento de verificação dos tipos e não em execução para
# evitar circular import.
if TYPE_CHECKING:
    from dundie_api.models.user import User


# Classe 'Transaction' que representa a tabela 'Transaction' no banco de dados.
class Transaction(SQLModel, table=True):
    """Represent the Transaction Model"""

    # Campo identificador da transação.
    id: Optional[int] = Field(default=None, primary_key=True)
    # Campo identificador do usuário que está recebendo os pontos.
    user_id: int = Field(foreign_key="user.id", nullable=False)
    # Campo identificador do usuário que está enviando os pontos.
    from_id: int = Field(foreign_key="user.id", nullable=False)
    # Campo que armazena a quantidade de pontos transferidos.
    value: int = Field(nullable=False)

    # Campo que armazena a data e a hora em que a transação foi realizada.
    # 'default_factory' atribui, de forma automática, qual o valor do campo
    # ao criar uma transação.
    # 'sa_column' está definindo que esse campo de date e hora possui timezone
    # ativada, dessa forma, ele considera o UTC.
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Mesmo caso dos campos de relação na tabela 'User'. Mas esse campo popula o campo
    # 'incomes' na tabela do usuário, para acessar as entradas de pontos dele.
    # Mesmo JOIN utilizado na outra tabela.
    user: Optional["User"] = Relationship(
        back_populates="incomes",
        sa_relationship_kwargs={"primaryjoin": "Transaction.user_id == User.id"},
    )

    # Mesmo caso dos campos de relação na tabela 'User'. Mas esse campo popula o campo
    # 'expenses' na tabela do usuário, para acessar as saídas de pontos dele.
    # Mesmo JOIN utilizado na outra tabela.
    from_user: Optional["User"] = Relationship(
        back_populates="expenses",
        sa_relationship_kwargs={"primaryjoin": "Transaction.from_id == User.id"},
    )


# Classe que representa a tabela 'Balance' no banco de dados.
class Balance(SQLModel, table=True):
    """Store the balance of a user account"""

    # Campo que define o identificador dessa tabela, que também representa qual o usuário.
    user_id: int = Field(
        foreign_key="user.id", nullable=False, primary_key=True, unique=True
    )
    # Campo que armazena o valor do saldo atual do usuário.
    value: int = Field(nullable=False)

    # Campo que armazena o tempo em que o registro for modificado. Também possui o timezone ativado.
    # e ele, por ter a propriedade 'onupdate' definida, cada vez que o saldo do usuário for alterado
    # ele vai atribuir um novo valor a este campo, que seria a data no momento da alteração.
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )

    # Campo para declarar a relação entre as tabelas 'User' e 'Balance', popula o campo '_balance' na tabela do usuário.
    user: Optional["User"] = Relationship(back_populates="_balance")
