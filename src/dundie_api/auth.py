"""Token based auth."""

# Biblioteca para trabalhar com data e hora.
from datetime import UTC, datetime, timedelta

# classe para criar uma função parcial a partir de outra função.
from functools import partial

# Type Annotation para um objeto do tipo chamável/invocável.
from typing import Callable

# Classe de exceção HTTP principal do FastAPI e módulo 'status' que contém
# todos os códigos de estado/resposta do HTTP.
from fastapi import HTTPException, status
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
def get_current_user(token: str):
    # Variável que representa uma exceção HTTP.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

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

    # Após todas as validações, retorna o usuário, caso tudo for validado com sucesso.
    return user


# Função para validar o token invocando a função 'get_current_user' e retornar os dados
# do usuário.
# TODO: Move to just one function to validate with 'get_current_user'.
def validate_token(token: str):
    user = get_current_user(token=token)
    return user
