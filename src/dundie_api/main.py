from fastapi import FastAPI, Request
from dundie_api.routes import main_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="dundie-api",
    version="0.1.0",
    description="dundie-api is a API for Dundie Rewards CLI Project.",
)

# Todos os middlewares aqui serão adicionados em todas as rotas da API.

# Adicionando uma middleware para o esquema HTTP usando o decorator.
@app.middleware("http")
# Função qualquer que adiciona um header apenas para estudo.
# A função `make_response` é uma função de callback apenas para processar
# o request e criar o response.
async def add_new_header(request: Request, make_response):
    # Processando o request, utiliza o await pois é uma operação que
    # deve ser concluída antes de seguir.
    # Qualquer processamento diretamente no request deve ser feito antes
    # dessa linha, pois é aqui que cria o objeto response.
    response = await make_response(request)

    # Adicionando um header qualquer no response
    response.headers["X-Qualquer-Coisa"] = "456"
    # Retornando o objeto response para que o ciclo de vida dele
    # continue. Obrigatório!
    return response

# Adicionando um middleware diretamente com a função
app.add_middleware(
    # Adicionando a middleware do CORS para permitir que outras
    # origens a partir do navegador possam solicitar o acesso a
    # API sem ter bloqueio.
    CORSMiddleware,
    # Lista de URLs de origem a serem permitidas.
    allow_origins=[
        "http://localhost:8001",
        "http://localhost"
    ],
    # Permite o navegador incluir credenciais de usuário, como cookies.
    allow_credentials=True,
    # Lista de métodos HTTP permitidos, ao usar *, permite todos.
    allow_methods=["*"],
    # Lista de headers permitidos na request, ao usar *, permite todos.
    allow_headers=["*"]
)

# Incluindo o router principal, este router armazena todos os outros subrouters
# criados.
app.include_router(main_router)
