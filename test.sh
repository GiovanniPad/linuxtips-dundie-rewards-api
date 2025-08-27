#!/usr/bin/bash

# Subindo os containers para testes usando o banco de dados de testes.
DUNDIE_DB=dundie_test docker compose up -d

# Aguardando 5 segundos para que os containers estejam prontos.
sleep 5

# Limpando o banco de dados de testes existente e garantindo que não
# tenha nenhuma migration nele, que ele esteja em um estado limpo.
docker compose exec api uv run dundie reset-db -f
docker compose exec api uv run alembic stamp base

# Aplicando todas as migrations com o banco de dados vazio.
docker compose exec api uv run alembic upgrade head

# Rodando os testes com o pytest
docker compose exec api uv run pytest -v -l --tb=short --maxfail=1 tests/

# Encerramento e apagando o ambiente de testes, junto com os volumes anônimos criados.
docker compose down
docker volume prune -f