"""Token based auth"""

# Biblioteca para trabalhar com data e hora.
from datetime import timedelta, datetime, timezone

# Classe para marcar algo como opcional (None)
from typing import Optional

# Biblioteca para gerar e validar JWT (PyJWT)
import jwt

# classe para criar uma função parcial a partir de outra função.
from functools import partial

# Variável de configurações da API.
from dundie_api.config import settings

# Chave secreta e algoritmo usado para gerar o JWT.
SECRET_KEY = settings.security.secret_key  # type: ignore
ALGORITHM = settings.security.algorithm  # type: ignore


# Função para gerar um JWT encriptografado.
# 'data' é o dicionário com o payload.
# 'expires_delta' é o tempo de validade do token.
# 'scope' define para qual função o token vai ser usado.
def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None, scope: str = "access_token"
) -> str:
    """Creates a JWT Token from user data

    scope: access_token or refresh_token
    """

    # Faz uma cópia dos dados para criar o JWT sem alterar os dados originais.
    to_encode = data.copy()

    # Se o tempo de expiração for especificado, é calculado o tempo usando ele.
    # Caso contrário, o tempo de expiração padrão será de 15 minutos.
    if expires_delta:
        # Pega o horário atual e soma com o tempo de expiração 'timedelta' inserido.
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Pega o horário atual e soma com o tempo de expiração 'timedelta' de 15 minutos.
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Inclui nas informações para criar o token, o tempo de expiração do token e o escopo dele.
    to_encode.update({"exp": expire, "scope": scope})

    # Cria o token JWT, usando o payload, secret key e o algoritmo para encriptografar.
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,  # type: ignore
        algorithm=ALGORITHM,  # type: ignore
    )

    # Retorna o token.
    return encoded_jwt


# Cria uma função nova (parcial) com base na função 'create_access_token' alterando
# o parâmetro 'scope' para "refresh_token". Evita-se código repetido. É opcional, pode ser
# passado via parâmetro.
create_refresh_token = partial(create_access_token, scope="refresh_token")
