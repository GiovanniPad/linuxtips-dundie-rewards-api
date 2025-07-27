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


# Simulando um Session Auth
################

from fastapi import Depends, Request, HTTPException, Response  # noqa: E402
from fastapi.responses import RedirectResponse  # noqa: E402

# Simulando um SESSION ID aleatório.
RANDOM_SESSION_ID = "bafgaecva"
# Simulando um usuário do banco de dados.
USER_CORRECT = ("admin", "admin")
# Simulando um banco de dados para sessões.
SESSION_DB = {}


# Verifica se o usuário tem uma sessão válida.
def get_auth_user(request: Request):
    """Verify that user has a valid session"""
    # Adquire a sessão dos cookies.
    session_id = request.cookies.get("Authorization")
    # Se a sessão não existir retorna um erro 401.
    if not session_id:
        raise HTTPException(status_code=401)
    # Se o SESSION ID não existir no banco de dados de sessões
    # retorna um erro 403.
    if session_id not in SESSION_DB:
        raise HTTPException(status_code=403)
    return True


# Rota que simula um login de usuário ussando sessão
@app.post("/login")
async def login(username: str, password: str):
    """/login?username=test&password=1234 !!!!ERRADO"""

    # Verifica se o usuário e a senha são válidos.
    allow = (username, password) == USER_CORRECT
    # Se não forem válidos retorna uma exceção de "sem autorização".
    if allow is False:
        raise HTTPException(status_code=401)
    # Cria uma response e redireciona para a rota "/", o status code 302 é obrigatório
    # para redirecionar automaticamente.
    response = RedirectResponse("/", status_code=302)
    # Define o cookie com o SESSION ID do usuário.
    response.set_cookie(key="Authorization", value=RANDOM_SESSION_ID)
    # Armazena o SESSION ID no banco de dados de sessão no servidor.
    SESSION_DB[RANDOM_SESSION_ID] = username
    # Resposta a response.
    return response


# Rota para deslogar o usuário.
@app.post("/logout")
async def logout(response: Response):
    # Deleta o cookie com o SESSION ID do lado do usuário.
    response.delete_cookie(key="Authorization")
    # Deleta o SESSION ID do banco de dados de sessão no servidor.
    SESSION_DB.pop(RANDOM_SESSION_ID, None)
    # Resposta indicando o logout.
    return {"status": "logged out"}


# Rota fictícia que depende do usuário estar autenticado.
# Para proteger a rota com autenticação utiliza-se dependencies e Depends.
@app.get("/", dependencies=[Depends(get_auth_user)])
async def secret():
    return {"secret": "info"}
