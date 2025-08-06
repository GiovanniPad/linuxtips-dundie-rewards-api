from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from dundie_api.auth import (
    RefreshToken,
    Token,
    User,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_user,
    validate_token,
)
from dundie_api.config import settings

# Tempo de expiração do token, adquiridos das configurações.
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes  # type: ignore
REFRESH_TOKEN_EXPIRE_MINUTES = settings.security.refresh_token_expire_minutes  # type: ignore

# Criando um router para incluir as rotas de autenticação.
router = APIRouter()


# View que o usuário chama para adquirir um novo token.
# Possui o modelo de resposta 'Token'.
@router.post("/token", response_model=Token)
# 'form_data' é a variável responsável por armazenar e realizar o parsing dos dados
# enviados através do formulário de login, o 'OAuth2PasswordRequestForm' é apenas uma
# classe para coletar o 'username' e a senha do usuário durante a requisição e ela
# também define o serialização das informações de forma correta, aplicando filtros.
# 'Depends' indica que 'form_data' é uma dependência dessa rota.
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Autentica o usuário passando o seu 'username' e senha.
    user = authenticate_user(get_user, form_data.username, form_data.password)

    # Se o usuário não for válido ou não for uma instância de 'User' exibe um erro
    # do tipo 401 (Não autorizado), informando que as credenciais estão incorretas.
    if not user or not isinstance(user, User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Define o tempo de expiração do token usando uma representação de tempo.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # type: ignore
    # Cria o access token com o 'username' do usuário e 'fresh=True' indicando que é um token novo.
    # Também define o tempo de expiração do token de acesso.
    access_token = create_access_token(
        data={"sub": user.username, "fresh": True}, expires_delta=access_token_expires
    )

    # Mesmo procedimento anterior, a diferença é que esse token é o refresh token. Nesse token
    # não vai a informação 'fresh'.
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)  # type: ignore
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    # Retorna os tokens gerados e qual o tipo dos tokens.
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# View para atualizar o tempo de expiração do token de acesso usando o refresh token.
@router.post("/refresh_token", response_model=Token)
# Recebe 'form_data' com a classe de modelagem para serialização 'RefreshToken' indicando
# as validações e campos necessários.
async def refresh_token(form_data: RefreshToken):
    # Valida o refresh token para ver se é um token válido.
    # await é usado pois é preciso aguardar esse processo concluir para continuar o restante
    # do código.
    user = await validate_token(token=form_data.refresh_token)

    # Cria um novo token de acesso com as mesmas informações, porém dessa vez 'fresh' é
    # False, indicando que não é um token novo mais, mas sim um renovado.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # type: ignore
    access_token = create_access_token(
        data={"sub": user.username, "fresh": False},
        expires_delta=access_token_expires,
    )

    # Cria e atualiza o refresh token também
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)  # type: ignore
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    # Retorna os novos tokens criados.
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
