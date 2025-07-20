"""Database connection"""

from sqlmodel import create_engine, Session
from .config import settings
from fastapi import Depends

# Criando o motor de conexão (engine) para se conectar ao banco de dados,
# com as configurações sendo passadas do arquivo de config do Dynaconf.
engine = create_engine(
    settings.db.uri,  # type: ignore
    echo=settings.db.echo,  # type: ignore
    connect_args=settings.db.connect_args,  # type: ignore
)


# Criando uma função que vai agir como uma dependência da aplicação para
# disponibilizar uma sessão de conexão com o banco de dados para todas as
# rotas que adicionar ela.
def get_session():
    with Session(engine) as session:
        yield session


# Atribui a dependência a uma variável para melhor uso.
# A função 'Depends' que é usada para declara uma dependência.
# A dependência precisa ser callable, ou seja, capaz de ser chamada.
ActiveSession = Depends(get_session)
