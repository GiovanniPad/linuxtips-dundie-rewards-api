from fastapi import APIRouter
from dundie_api.routes.user import router as user_router
from dundie_api.routes.auth import router as auth_router

# Criando um main router para incluir todas os conjuntos de subrotas
# criados.
main_router = APIRouter()

# Incluindo a rota das operações para os usuários com o prefixo '/user' e com
# tag 'user', para melhor leitura na documentação.
main_router.include_router(user_router, prefix="/user", tags=["user"])
# Incluindo as rotas de autenticação de usuários.
main_router.include_router(auth_router, tags=["auth"])
