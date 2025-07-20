from sqlmodel import Session, select
from dundie_api.models import User
from dundie_api.serializers import UserResponse
from dundie_api.db import ActiveSession

from fastapi import APIRouter

# Criando um conjunto de rotas individuais, neste caso, elas são
# responsáveis pelas rotas de usuários.
router = APIRouter()


# Rota 'GET' para listar todos os usuários cadastrados no banco de dados.
# Ela possui um modelo de resposta indicando que vai ser retornado uma
# lista de UserResponse, que é o serializer 'UserResponse'.
# E possui uma dependência atrelada, que é da sessão do banco de dados 'session'.
@router.get("/", response_model=list[UserResponse])
async def list_users(*, session: Session = ActiveSession):
    """List all users from database"""
    # Selecionando todos os usuários da tabela 'user'.
    users = session.exec(select(User)).all()

    # Retornando a lista de usuários.
    # Por ter um modelo de response indicado o framework vai
    # exibir, filtrar e aplicar todas as validações definidas no
    # modelo de response em cima do modelo principal 'User'.
    return users
