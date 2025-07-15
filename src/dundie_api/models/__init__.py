from sqlmodel import SQLModel
from .user import User

# Variável especial que, ao importar todo o pacote 'models', também
# importa automaticamente objetos declarados nesta lista. Nesta caso,
# estamos importando a classe User e a classe SQLModel ao chamar
# 'import dundie_api.models' ou então torna possível importar individualmente
# utilizando o 'from dundie_api.models *'
__all__ = ["User", "SQLModel"]
