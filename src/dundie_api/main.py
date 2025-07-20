from fastapi import FastAPI
from dundie_api.routers.user import router as user_router

app = FastAPI(
    title="dundie-api",
    version="0.1.0",
    description="dundie-api is a API for Dundie Rewards CLI Project.",
)

# Incluindo a rotas do usuário na aplicação principal, atribuindo um prefixo
# '/user' para todas as rotas criadas do usuário e uma tag 'user' para melhor
# exibição na documentação.
app.include_router(user_router, prefix="/user", tags=["user"])