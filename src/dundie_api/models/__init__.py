# Classe principal da biblioteca SQLModel.
from sqlmodel import SQLModel

# Model User.
from .user import User

# Variável especial que, ao importar todo o pacote 'models', também
# importa automaticamente objetos declarados nesta lista. Neste caso,
# estamos importando apenas as classes User e a classe SQLModel
# ao chamar 'from dundie_api.models import *'.
__all__ = ["User", "SQLModel"]
