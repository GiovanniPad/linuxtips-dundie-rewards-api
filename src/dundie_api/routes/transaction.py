from fastapi import APIRouter, Body, HTTPException, Depends
from dundie_api.auth import AuthenticatedUser
from dundie_api.db import ActiveSession
from dundie_api.models import User
from dundie_api.serializers.transaction import TransactionResponse
from dundie_api.tasks.transaction import add_transaction, TransactionError, Transaction
from sqlmodel import select, Session, text

from sqlalchemy.orm import aliased

from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page, Params

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


# Rota para listar as transações dos usuários, esta rota contém paginação com 'Page' e o
# modelo de resposta 'TransactionResponse'. Ela também contém filtros e ordenação pela data
# da transação.
@router.get("/", response_model=Page[TransactionResponse])
# 'current_user' indica o usuário autenticado.
# 'session' é a sessão de conexão com o banco de dados.
# 'params' são os parâmetros da funcionalidade de paginação, como o número da página e
# o limite de registros por página.
# 'user' é o filtro opcional para exibir as transações que o usuário recebeu pontos.
# 'from_user' é o filtro opcional para exibir as transações que o usuário enviou pontos.
# 'order_by' é o campo de ordenação pela data, podendo ser ascendente e decrescente.
async def list_transactions(
    *,
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
    params: Params = Depends(),
    user: str | None = None,
    from_user: str | None = None,
    order_by: str | None = None,
):
    """List all transactions."""

    # Query base, seleciona todas as transações.
    query = select(Transaction)

    # Caso o filtro 'user' estiver definido, exibe todas as transações que o usuário
    # em questão recebeu pontos.
    if user:
        # Adiciona na query a cláusula JOIN, buscando as transações que o usuário foi
        # o usuário que recebeu os pontos.
        query = query.join(User, Transaction.user_id == User.id).where(
            User.username == user
        )

    # Caso o filtro 'from_user' estiver definido, exibe todas as transações em que o
    # usuário em questão enviou pontos.
    if from_user:
        # Cria um alias para o model User, permitindo adicionar mais um JOIN, caso ambos
        # os filtros 'user' e 'from_user' estejam definidos, caso contrário vai gerar um
        # erro. O alias 'FromUser' aponta também para a tabela 'User' mas permite que o
        # SQLAlchemy faça as operações de forma correta e entenda o que está sendo pedido.
        FromUser = aliased(User)

        # Adiciona na query a cláusula JOIN, buscando as transações que o usuário foi
        # o usuário que enviou os pontos.
        query = query.join(FromUser, Transaction.from_id == FromUser.id).where(
            FromUser.username == from_user
        )

    # Cláusula de guarda onde permite que usuários que não são super usuários vejam apenas as
    # suas próprias transações, sendo elas de entrada ou saída.
    if not current_user.superuser:
        # Adiciona uma cláusula WHERE onde busca todas as transações em que o usuário ou enviou
        # pontos ou recebeu pontos.
        query = query.where(
            (Transaction.user_id == current_user.id)
            | (Transaction.from_id == current_user.id)
        )

    # Caso o campo de ordenação esteja definido, realiza a ordenação decrescente ou crescente usando
    # o campo 'date' da tabela. Quando especificado '-date' realiza a ordenação decrescente.
    if order_by:
        # Utiliza a função 'text' para construir um texto que vai representar uma parte ou então uma
        # query SQL completa. Neste caso, se tiver o sinal '-', a ordenação vai ser decrescente, caso
        # contrário, crescente.
        order_text = text(
            order_by.replace("-", "") + " " + ("desc" if "-" in order_by else "asc")
        )
        # Compõe a query base com o SQL para realizar a ordenação.
        query = query.order_by(order_text)

    # Retorna todas as transações de forma paginada. Para isso é preciso passar a sessão de conexão com
    # o banco de dados, a query de seleção e os parâmetros (nº de páginas e nº de registros por página).
    return paginate(session=session, query=query, params=params)
