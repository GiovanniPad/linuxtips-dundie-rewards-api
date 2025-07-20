from fastapi import FastAPI
from dundie_api.routes import main_router

app = FastAPI(
    title="dundie-api",
    version="0.1.0",
    description="dundie-api is a API for Dundie Rewards CLI Project.",
)

# Incluindo o router principal, este router armazena todos os outros subrouters
# criados.
app.include_router(main_router)
