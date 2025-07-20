"""Database connection"""

from sqlmodel import create_engine, Session
from .config import settings
# Função que cria dependências.
from fastapi import Depends

# Criando o motor de conexão (engine) para se conectar ao banco de dados,
# com as configurações sendo passadas do arquivo de config do Dynaconf.
engine = create_engine(
    settings.db.uri,  # type: ignore
    echo=settings.db.echo,  # type: ignore
    connect_args=settings.db.connect_args,  # type: ignore
)


# Criando uma função que vai agir como uma dependência para as views.
def get_session():
    with Session(engine) as session:
        yield session


# Declarando as dependências com 'Depends' e atribuindo a uma variável
# para maior facilidade.
ActiveSession = Depends(get_session)
