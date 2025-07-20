from fastapi import FastAPI
from dundie_api.models import User
from sqlmodel import select, Session
from dundie_api.serializers import UserResponse
from dundie_api.db import ActiveSession


app = FastAPI(
    title="dundie-api",
    version="0.1.0",
    description="dundie-api is a API for Dundie Rewards CLI Project.",
)

# Views que retorna o primeiro usuário cadastrado no banco de dados.
# Usa um response model, que é o model de resposta do usuário (User).
# E utiliza uma dependência, que é a dependência para disponibilizar
# uma sessão conectada com o banco de dados, evitando código repetido.
@app.get("/", response_model=UserResponse)
def hello(session: Session = ActiveSession):
    return session.exec(select(User)).first()
