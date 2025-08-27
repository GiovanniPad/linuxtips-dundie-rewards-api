import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from dundie_api.main import app
from dundie_api.cli import create_user

# Definindo a URI do banco de dados de testes no ambiente, para garantir
# que o banco correto vai ser utilizado.
os.environ["DUNDIE_DB__uri"] == "postgresql://postgres:postgres@db:5432/dundie_test"


# Fixture que vai ser aplicada a toda função de testes, ela
# tem a função de criar e retornar um cliente de testes não autenticado.
@pytest.fixture(scope="function")
def api_client():
    """Unauthenticated test client"""
    return TestClient(app)


# Função para criar um cliente de API de teste autenticado
def create_api_client_authenticated(username, dept="sales", create=True):
    """Create a new api client authenticated for the specified user."""
    # Variável de controle que define se o cliente (usuário) vai ser criado ou não.
    if create:
        try:
            # Cria o usuário.
            create_user(
                name=username, email=f"{username}@dm.com", password=username, dept=dept
            )
        except IntegrityError:
            pass

    # Cria um cliente de testes.
    client = TestClient(app)

    # Faz uma requisição POST para a URL de gerar um JWT para autenticação.
    token = client.post(
        "/token",
        data={"username": username, "password": username},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]

    # Passa o token para a configuração de headers do cliente de testes. Dessa
    # forma, não é preciso ficar autenticando toda vez.
    client.headers["Authorization"] = f"Bearer {token}"

    # Retorna a instância do cliente já autenticado.
    return client


# Fixtures são funções do Pytest que permite realizar determinadas ações
# ou configurações necessárias para preparar o ambiente de testes, são muito
# utilizadas para casos em que há muito código repetido.

# Neste caso, todas as fixtures são criadas a nível de escopo de função, quer dizer
# que elas podem ser utilizadas em cada função de teste.


# Fixture para criar e retornar um cliente de api do tipo "admin".
@pytest.fixture(scope="function")
def api_client_admin():
    return create_api_client_authenticated("admin", create=False)


# Fixture para criar e retornar um cliente de api que é do departamento
# de gerência.
@pytest.fixture(scope="function")
def api_client_user1():
    return create_api_client_authenticated("user1", dept="management")


# Fixture para criar e retornar um cliente de api qualquer.
@pytest.fixture(scope="function")
def api_client_user2():
    return create_api_client_authenticated("user2")


# Fixture para criar e retornar um cliente de api qualquer.
@pytest.fixture(scope="function")
def api_client_user3():
    return create_api_client_authenticated("user3")
