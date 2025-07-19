# Importando os serializers do usuário.
from dundie_api.serializers.user import UserRequest, UserResponse

# Variável especial que, ao importar todo o pacote 'serializers', também
# importa automaticamente objetos declarados nesta lista. Neste caso,
# estamos importando apenas as classes UserRequest e a classe UserResponse
# ao chamar 'from dundie_api.serializers import *'.
__all__ = ["UserResponse", "UserRequest"]
