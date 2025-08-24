from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


# Serializer para serializar a resposta do model Transaction.
class TransactionResponse(BaseModel):
    # ID da transação.
    id: int
    # Valor da transação.
    value: int
    # Data e hora da transação.
    date: datetime

    # Usuário que recebeu os pontos, este campo vai ser definido depois.
    user: Optional[str] = None
    # usuário que envio os pontos, este campo também vai ser definido depois.
    from_user: Optional[str] = None

    # Validando os campos 'user' e 'from_user' antes do serializer ser instanciado e
    # os dados validados. Para ser um validador é preciso ser um método da classe.
    @field_validator("user", "from_user", mode="before")
    @classmethod
    def get_usernames(cls, value) -> str | None:
        # Se o usuário estiver definido ('value') por conta do operador 'and' vai ser
        # retornado o último valor verdadeiro, no caso, o seu 'username'. Caso ele não
        # existir, vai ser retornado None, por conta que o 'and' ao encontrar um valor
        # negativo, ele retorna ele de imediato.
        return value and value.username

    # TODO: Serialize date field to correct time.
