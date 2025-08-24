from fastapi import APIRouter, Body, HTTPException
from dundie_api.auth import AuthenticatedUser
from dundie_api.db import ActiveSession
from dundie_api.models import User
from dundie_api.tasks.transaction import add_transaction, TransactionError
from sqlmodel import select, Session

router = APIRouter()


# Rota para realizar uma transação.
# 'status_code' indica quais os possíveis códigos de status que podem ser retornados.
@router.post("/{username}", status_code=201)
# 'username' é o usuário que vai receber os pontos.
# 'value' é a quantidade de pontos a serem transferidos.
# 'current_user' é o usuário logado e também representa o usuário que vai enviar os pontos.
# 'session' é a sessão de conexão com o banco de dados.
async def create_transaction(
    *,
    username: str,
    value: int = Body(embed=True),
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
):
    """Add a new transaction to the specified user."""

    # Seleciona o usuário a receber os pontos do banco de dados.
    user = session.exec(select(User).where(User.username == username)).first()
    # Caso o usuário não existir, emite uma exceção HTTP indicando que ele não foi encontrado.
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Tenta criar uma transação de transferência de pontos.
    try:
        add_transaction(user=user, from_user=current_user, value=value, session=session)

    # Caso ocorra algum erro, ele é interceptado e a mensagem de erro é exibida.
    except TransactionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Chegando aqui, a transação já foi feita com sucesso, exibindo uma mensagem de sucesso.
    return {"message": "Transaction added"}
