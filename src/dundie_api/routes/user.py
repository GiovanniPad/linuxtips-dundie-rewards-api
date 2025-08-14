from sqlmodel import Session, select
from dundie_api.models import User
from dundie_api.serializers.user import (
    UserResponse,
    UserRequest,
    UserProfilePatchRequest,
)
from dundie_api.db import ActiveSession
from dundie_api.auth import AuthenticatedUser, SuperUser

from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, HTTPException, status

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

    # LBYL - Verifica antes se o email inserido já está registro para outro
    # usuário antes de adicionar o usuário no banco de dados.
    # if session.exec(select(User).where(User.email == user.email)).first():
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="User email already exists."
    #     )

    # Converte e valida o serializador de entrada 'UserRequest' para o modelo 'User',
    # que é o modelo de conexão ao banco de dados. Todos os campos são validados.
    db_user = User.model_validate(user)

    # Adiciona o usuário a sessão de conexão, para criá-lo.
    session.add(db_user)

    # Tenta criar o usuário no banco de dados antes de tratar qualquer tipo, apenas
    # quando der algum erro, vai cair no bloco de except para serem tratados.
    try:
        # Executa todos os comandos presentes na sessão, refletindo no banco de dados.
        session.commit()

    # IntegrityError indica qualquer tipo de erro que possa ocorrer relacionado ao banco de dados.
    except IntegrityError:
        # Sempre utilizar o 'HTTPException' para APIs REST.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database IntegrityError",
        )

    # Atualiza os dados do usuário instanciado na rota com os dados atualizados do
    # banco de dados, mantendo a conformidade.
    session.refresh(db_user)

    # Retorna o usuário criado, aqui é feito a serialização dos dados de acordo com
    # o serializador 'UserResponse'.
    return db_user


# Rota para realizar o update parcial dos dados de um usuário. O usuário é selecionado
# através do seu 'username' e o 'patch' define o tipo da rota, no caso, update parcial.
# 'response_model' indica o modelo de serialização de resposta da requisição.
@router.patch("/{username}/", response_model=UserResponse)
# 'session' é a seção de conexão com o banco de dados.
# 'patch_data' são os dados a serem alterados.
# 'current_user' é o usuário atual autenticado, neste caso, a dependência está sendo
# declarada dentro da função, pois vai ser necessário acessar a instância do usuário autenticado.
# 'username' é o identificador do usuário a ter seus dados parcialmente alterados.
async def update_user(
    *,
    session: Session = ActiveSession,
    patch_data: UserProfilePatchRequest,
    current_user: User = AuthenticatedUser,
    username: str,
):
    # Busca o usuário no banco de dados atráves de seu 'username'.
    user = session.exec(select(User).where(User.username == username)).first()

    # Se nenhum usuário for encontrado invoca uma exceção HTTP do tipo 404
    # indicando que o usuário não foi encontrado.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    # Apenas o próprio usuário ou o superuser pode realizar a operação
    # de alterar parcialmente os dados.
    # Caso não for o próprio usuário e não for um superuser, invoca uma
    # exceção HTTP do tipo 403, que indica não permitido.
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile.",
        )

    # Verifica se o campo 'avatar' não está vazio para evitar, caso ele não seja
    # passado, de subscrever o valor atual do campo no banco de dados.
    if patch_data.avatar is not None:
        user.avatar = patch_data.avatar

    # Mesmo verificação do campo 'avatar', mas agora para o campo 'bio'.
    if patch_data.bio is not None:
        user.bio = patch_data.bio

    # Adiciona a instância modificada do usuário na sessão.
    session.add(user)

    # TODO: Treat Exceptions
    # Confirma as mudanças, refletindo as alterações no banco de dados.
    session.commit()

    # Atualiza a instância do usuário para refletir informações preenchidas
    # no nível do banco de dados na instância atual.
    session.refresh(user)

    # Retorna a instância do usuário já atualizada.
    return user
