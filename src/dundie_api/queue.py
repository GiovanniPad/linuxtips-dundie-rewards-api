from redis import Redis
from rq import Queue
from dundie_api.config import settings

# Criando uma instância que representa um banco de dados Redis.
redis = Redis(host=settings.redis.host, port=settings.redis.port)

# Criando uma fila de tasks com o RQ e apontando a instância do Redis para ela.
queue = Queue(connection=redis)
