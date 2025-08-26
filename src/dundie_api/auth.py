"""Token based auth."""

# Biblioteca para trabalhar com data e hora.
from datetime import UTC, datetime, timedelta

# classe para criar uma função parcial a partir de outra função.
from functools import partial

# Type Annotation para um objeto do tipo chamável/invocável.
from typing import Callable, Optional

# Classe de exceção HTTP principal do FastAPI e módulo 'status' que contém
# todos os códigos de estado/resposta do HTTP.
from fastapi import Depends, HTTPException, Request, status

# Classe para autenticação usando o fluxo OAuth2 com um token JWT.
from fastapi.security import OAuth2PasswordBearer

# Classe para criar modelos do Pydantic.
from pydantic import BaseModel

# Biblioteca para gerar e validar JWT (PyJWT)
import jwt

# Classe para representar um erro de validação de um token.
from jwt import PyJWTError

# Variável de configurações da API.
from dundie_api.config import settings

# Função para verificar a senha.
from dundie_api.security import verify_password

# Model 'User".
from dundie_api.models import User

# Engine para conexão ao banco de dados.
from dundie_api.db import engine

# Objetos para fazer querys no banco de dados.
from sqlmodel import select, Session

# Chave secreta e algoritmo usado para gerar o JWT.
SECRET_KEY = settings.security.secret_key  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]
ALGORITHM = settings.security.algorithm  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]

# Criando a instância do esquema de autenticação, através dela que vai ser gerado todo o fluxo de autenticação
# usando JWT, incluindo formulários e validações.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Modelos para representar o Token, RefreshToken e o Payload (conteúdo).


# TODO: Move all validation to a unique Token Model later.
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class Payload(BaseModel):
    username: str | None = None


# Função para gerar um JWT encriptografado.
# 'data' é o dicionário com o payload.
# 'expires_delta' é o tempo de validade do token.
# 'scope' define para qual função o token vai ser usado.
def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
    scope: str = "access_token",
) -> str:
    """Create a JWT Token from user data.

    scope: access_token or refresh_token
    """
    # Faz uma cópia dos dados para criar o JWT sem alterar os dados originais.
    to_encode = data.copy()

    # Se o tempo de expiração for especificado, é calculado o tempo usando ele.
    # Caso contrário, o tempo de expiração padrão será de 15 minutos.
    if expires_delta:
        # Pega o horário atual e soma com o tempo de expiração 'timedelta' inserido.
        expire = datetime.now(UTC) + expires_delta
    else:
        # Pega o horário atual e soma com o tempo de expiração
        # 'timedelta' de 15 minutos.
        expire = datetime.now(UTC) + timedelta(minutes=15)

    # Inclui nas informações para criar o token,
    # o tempo de expiraçãodo token e o escopo dele.
    to_encode.update({"exp": expire, "scope": scope})

    # Cria o token JWT, usando o payload, secret key e o algoritmo para encriptografar.
    return jwt.encode(
        to_encode,
        SECRET_KEY,  # pyright: ignore[reportArgumentType]
        algorithm=ALGORITHM,  # pyright: ignore[reportArgumentType]
    )


# Cria uma função nova (parcial) com base na função 'create_access_token' alterando
# o parâmetro 'scope' para "refresh_token". Evita-se código repetido.
# É opcional, pode ser passado via parâmetro.
create_refresh_token = partial(create_access_token, scope="refresh_token")


# Função para autenticar um usuário.
# Recebe uma função 'get_user' para selecionar o usuário do banco de dados e
# recebe o 'username' e a senha ('password') do usuário.
def authenticate_user(
    get_user: Callable,
    username: str,
    password: str,
) -> User | bool:
    """Verify if user exists and password is correct."""

    # Seleciona o usuário no banco de dados através de seu username.
    user = get_user(username)

    # Se não encontrar nenhum usuário, retorna falso, indicando que o
    # usuário em questão não existe.
    if not user:
        return False

    # Valida a senha passada para ver se bate com a que está no banco de dados.
    # TODO: VerifyMismatchError
    if not verify_password(plain_password=password, hashed_password=user.password):
        return False

    # Caso todas as validações forem verdadeiras retorna o usuário e seus dados.
    return user


# Função para selecionar um usuário no banco de dados.
def get_user(username: str | None) -> User | None:
    # TODO: move to utils module or User model.
    # Monta a query para selecionar o usuário através de seu 'username'.
    query = select(User).where(User.username == username)
    # Abre uma sessão de conexão com o banco de dados.
    with Session(engine) as session:
        # Retorna o primeiro usuário encontrado no banco de dados.
        return session.exec(query).first()


# TODO: Move to pydantic model for direct validation (maybe).
# Função para validar se o payload está válido e decodificar o token.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    request: Request = None,  # pyright: ignore[reportArgumentType]
    fresh=False,
):
    """Get currentu ser authenticated."""
    # Variável que representa uma exceção HTTP.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Se há um objeto request recebido, verifica se o header 'authorization' está
    # presente usando o walrus operator, dessa forma, tanto a comparação quanto a
    # atribuição é realizada na mesma linha.
    # Caso o header 'authorization' estiver definido, ele tenta coletar o token
    # incluso na solicitação. Caso não for possível adquirir o token, invoca um
    # erro de credenciais inválidas.
    if request:
        if authorization := request.headers.get("authorization"):
            try:
                token = authorization.split(" ")[1]
            except IndexError:
                raise credentials_exception

    try:
        # Decodifica o token, retornando o payload.
        # É necessário a chave secreta e o algoritmo usado anteriormente.
        payload = jwt.decode(
            token,
            SECRET_KEY,  # pyright: ignore[reportArgumentType]
            algorithms=[ALGORITHM],  # pyright: ignore[reportArgumentType]
        )

        # Seleciona o 'username' do usuário.
        username: str = payload.get("sub")

        # Verifica se o 'username' está vazio, se estiver invoca um erro
        # de validação de credenciais.
        if username is None:
            raise credentials_exception

        # Cria uma instância da classe 'Payload' do Pydantic para representar
        # os dados do token.
        token_data = Payload(username=username)

    # Caso a decodificação do token falhar, essa exceção é capturada.
    except PyJWTError:
        # Invoca uma exceção de erro de validação de credenciais.
        raise credentials_exception

    # Seleciona o usuário no banco de dados através do 'username'.
    user = get_user(username=token_data.username)

    # Se não encontrar nenhum usuário, invoca um erro de validação de credenciais.
    if user is None:
        raise credentials_exception

    # Se for um novo token, é no payload a chave 'fresh' não estiver definida e o usuário
    # não for um super usuário, retorna um erro de credenciais.
    if fresh and (not payload["fresh"] and not user.superuser):
        raise credentials_exception

    # Após todas as validações, retorna o usuário, caso tudo for validado com sucesso.
    return user


# Função para validar o token invocando a função 'get_current_user' e retornar os dados
# do usuário.
# TODO: Move to just one function to validate with 'get_current_user'.
# 'Depends' indica que o token depende do esquema do oauth2, dessa forma
# as validações são realizadas.
async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    user = get_current_user(token=token)
    return user


# Função wrapper, que encapsula a função 'get_current_user' para funcionar de forma
# assíncrona nas chamadas da API.
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Wrap the sync get_active_user for async calls."""
    return current_user


# Cria uma dependência e atribui a variável 'AuthenticatedUser' para uso facilitado
# nas views.
AuthenticatedUser = Depends(get_current_active_user)


# Função para verificar se o usuário logado é um superusuário.
async def get_current_super_user(current_user: User = Depends(get_current_user)):
    # Se o usuário logado não for um superusuário retorna um erro 403.
    if not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a super user"
        )
    # Retorna o usuário, se ele for um superusuário.
    return current_user


# Cria uma dependência para ser usuada nas views para indicar que só
# superusuários podem acessá-la.
SuperUser = Depends(get_current_super_user)


# Função assíncrona que vai ser uma dependência, onde sua ação é de verificar
# se o usuário possui a devida permissão para realizar a troca de sua senha ou
# a senha de qualquer outro usuário.
# 'request' é o objeto da requisição com todos os dados, incluindo o de autenticação.
# 'pwd_reset_token' é o token opcional que vai ser utilizada pela UI para realizar
# a troca de senha.
# 'username' é o usuário que está sendo alterado.
async def get_user_if_change_password_is_allowed(
    *, request: Request, pwd_reset_token: None | str = None, username: str
):
    """Return user if one of the conditions is met.
    1. There is a pwd_reset_token passed as query parameter and it is valid OR
    2. authenticated_user is superuser OR
    3. authenticated_user is User
    """

    # Buscando o usuário no banco de dados para alterar sua senha.
    target_user = get_user(username)

    # Se não encontrar nenhum registro, invoca uma exceção HTTP do tipo 404,
    # indicando que o usuário não foi encontrado.
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    # Se o token estiver definido, tenta validar se o token de resetar a senha é
    # válido e pertence ao usuário que está fazendo a alteração. Se sim, retorna
    # como True, se não, por invocar uma HTTPException, define como False.
    try:
        valid_pwd_reset_token = (
            get_current_user(token=pwd_reset_token or "") == target_user
        )
    except HTTPException:
        valid_pwd_reset_token = False

    # Tenta validar se o usuário autenticado é válido. Se for retorna o usuário, se não
    # retorna None.
    try:
        authenticated_user = get_current_user(token="", request=request)
    except HTTPException:
        authenticated_user = None

    # Verifica se alguma das expressões abaixo é verdadeira, caso qualquer uma delas forem
    # True, 'any' vai retornar True também, caso contrário, retorna False.
    if any(
        [
            valid_pwd_reset_token,
            authenticated_user and authenticated_user.superuser,
            authenticated_user and authenticated_user.id == target_user.id,
        ]
    ):
        # Caso passe em qualquer uma das regras acima impostas, retorna o usuário que vai
        # ter sua senha alterada
        return target_user

    # Caso não passe em nenhuma das validações de permissão, retorna uma exceção HTTP do tipo 403,
    # que determina que o usuário não tem permissão para fazer a troca da senha.
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to change this user's password.",
    )


# Cria uma dependência para atrelar a uma rota de alterar a senha, permitindo que as regras para
# alteração da senha seja executada de forma antecipada, antes mesmo de executar a função da view.
CanChangeUserPassword = Depends(get_user_if_change_password_is_allowed)


# Dependência para validar se o usuário possui a permissão para visualizar o campo de saldo dos
# usuários e o seu próprio saldo.
# 'request' é o objeto da requisição, 'show_balance' é um campo opcional que pode ser passado para
# informar se vai ou não exibir o saldo.
async def show_balance_field(
    *, request: Request, show_balance: Optional[bool] = False
) -> bool:
    """Return True if one of the condition is met.
    1. show_balance is True AND
    2. authenticated_user.superuser OR
    3. authenticated_user.username == username
    """
    # Se o campo for falso, não valida nada, apenas retorna que o campo 'balance' não vai ser exibido.
    if not show_balance:
        return False

    # Adquire o parâmetro 'username' a partir do caminho da rota para validação e verificar a permissão.
    username = request.path_params.get("username")

    # Tenta autenticar o usuário que está fazendo a requisição, caso consiga logar, armazena o usuário,
    # caso contrário, armazena como None.
    try:
        authenticated_user = get_current_user(token="", request=request)
    except HTTPException:
        authenticated_user = None

    # Valida as expressões abaixo, caso qualquer uma delas forem verdadeira, a função 'any' retorna True.
    # Permite o usuário acessar o saldo, caso ele esteja autenticado e também seja um super usuário ele tem permissão ou
    # caso ele esteja autenticado e esteja tentando visualizar seu próprio saldo também tem permissão, caso contrário
    # não tem permissão.
    if any(
        [
            authenticated_user and authenticated_user.superuser,
            authenticated_user and authenticated_user.username == username,
        ]
    ):
        return True

    # Caso ele não possua nenhum tipo de permissão, retorna False.
    return False


# Cria uma dependência para permitir a exibição do campo de saldo dos usuários nas
# rotas.
ShowBalanceField = Depends(show_balance_field)
