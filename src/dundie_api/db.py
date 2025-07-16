"""Database connection"""
from sqlmodel import create_engine
from .config import settings

# Criando o motor de conexão (engine) para se conectar ao banco de dados,
# com as configurações sendo passadas do arquivo de config do Dynaconf.
engine = create_engine(
    settings.db.uri, # type: ignore
    echo=settings.db.echo, # type: ignore
    connect_args=settings.db.connect_args, # type: ignore
)
