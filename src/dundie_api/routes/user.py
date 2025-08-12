from sqlmodel import Session, select
from dundie_api.models import User
from dundie_api.serializers import UserResponse, UserRequest
from dundie_api.db import ActiveSession
from dundie_api.auth import AuthenticatedUser, SuperUser

from fastapi import APIRouter, HTTPException

# Criando um conjunto de rotas individuais, neste caso, elas são
# responsáveis pelas rotas de usuários.
router = APIRouter()


# Rota 'GET' para listar todos os usuários cadastrados no banco de dados.
# Ela possui um modelo de resposta indicando que vai ser retornado uma
# lista de UserResponse, que é o serializer 'UserResponse'.
# E possui uma dependência atrelada, que é da sessão do banco de dados 'session'.
# Protengendo a rota com a dependência 'AuthenticatedUser' para que apenas usuários
# autenticados a chamem.
@router.get("/", response_model=list[UserResponse], dependencies=[AuthenticatedUser])
async def list_users(*, session: Session = ActiveSession):
    """List all users from database."""
    # Selecionando todos os usuários da tabela 'user'.
    users = session.exec(select(User)).all()

    # Retornando a lista de usuários.
    # Por ter um modelo de response indicado o framework vai
    # exibir, filtrar e aplicar todas as validações definidas no
    # modelo de response em cima do modelo principal 'User'.
    return users


# Criando uma rota para listar um usuário através de seu username, o 'username' está
# sendo passado através de um parâmetro pela URL (Path Parameter).
# O serializador de resposta desta rota é 'UserResponse'.
# Ela também recebe a dependência da sessão do banco de dados e o 'username' inserido
# na rota, através de injeção de dependência.
@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(*, session: Session = ActiveSession, username: str):
    """Get single user by username"""

    # Query para selecionar o usuário no banco de dados através de seu 'username'.
    query = select(User).where(User.username == username)

    # Executando a query SQL. 'first()' é usado para retornar a instância única do
    # usuário direta, sem ser uma lista.
    user = session.exec(query).first()

    # Verifica se o usuário existe no banco de dados, senão existir retorna uma
    # mensagem de erro.
    if not user:
        # Invoca uma exceção HTTP com código 404 (not found) e uma mensagem detalhada.
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    # Retorna o usuário encontrado no banco de dados, o framework já realiza a serialização
    # para o modelo de response UserResponse, desde que seja compatível.
    return user


# Rota para criar um novo usuário no banco de dados, recebe 'UserResponse' como modelo
# de resposta e 'status_code' indica quais os códigos HTTP que podem ser retornados.
# Recebe como injeção de dependência, a sessão do banco de dados (session) e o payload (user)
# que corresponde aos dados do usuário a ser criado.
# O payload é validado usando o serializador 'UserRequest'.
# Protegendo a rota com a dependência 'SuperUser' para que apenas superusuários acessem.
@router.post(
    "/", response_model=UserResponse, status_code=201, dependencies=[SuperUser]
)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Create a new user."""

    # Converte e valida o serializador de entrada 'UserRequest' para o modelo 'User',
    # que é o modelo de conexão ao banco de dados. Todos os campos são validados.
    db_user = User.model_validate(user)

    # Adiciona o usuário a sessão de conexão, para criá-lo.
    session.add(db_user)

    # Executa todos os comandos presentes na sessão, refletindo no banco de dados.
    session.commit()
    # Atualiza os dados do usuário instanciado na rota com os dados atualizados do
    # banco de dados, mantendo a conformidade.
    session.refresh(db_user)

    # Retorna o usuário criado, aqui é feito a serialização dos dados de acordo com
    # o serializador 'UserResponse'.
    return db_user
