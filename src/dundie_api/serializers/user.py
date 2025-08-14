# TODO: Create a core module and a UserBaseModel

# Biblioteca para criar classes que vão servir de serializadores para a API, com
# a possibilidade de validação e controle de exibição de campos.
from pydantic import BaseModel, field_validator, ValidationInfo, Field, model_validator

# Classe para definir que uma variável pode ser None, ou seja, opcional.
from typing import Optional

# Função para criar um hash da senha.
from dundie_api.security import get_password_hash

# Função para criar um username para o usuário.
from dundie_api.models.user import generate_username

from fastapi import HTTPException, status


# Classe que representa como vai ser o objeto de resposta para o cliente.
# Ela é um serializador para responder a chamadas, filtrando campos e
# realizando a validação
class UserResponse(BaseModel):
    """Serializer for send a response to the client."""

    # Campos que vão ser exibidos no objeto de resposta (Response) com os
    # seus tipos de dados definidos com Type Annotation, que serão usados
    # para validar e realizar o parsing.
    name: str
    username: str
    dept: str
    # Campos com 'Optional' são campos que podem ser None ou conter algum
    # tipo de valor definido. Nestes casos, ambos são Strings ou None.
    avatar: Optional[str] = None
    bio: Optional[str] = None
    currency: str


# Classe que define o serializador de Request, que será usado quando o usuário
# for criar uma nova instância de usuário no banco de dados.
# Possui suas próprias validações, requerente campos diferentes do serializer
# de resposta.
class UserRequest(BaseModel):
    """Serializar for get the user data from the client."""

    # Declarando os campos que serão obrigatórios a serem inseridos e seus tipos
    # de dados.
    name: str
    email: str
    dept: str
    password: str
    # Campos opcionais e que possuem valores padrão.
    # Todo campo que possui um valor padrão não é validado, por conta disso, a
    # opção 'validate_default' está como True, pois mesmo tendo um valor padrão
    # este campo precisa de validação.
    username: Optional[str] = Field(default=None, validate_default=True)
    # Outros campos opcionais, mas que não necessitam de validação.
    avatar: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    currency: str = Field(default="USD")

    # Decorator que indica que o campo 'username' vai ser validado antes de instanciar
    # o objeto UserRequest. É necessário que ele seja um método, por isso, '@classmethod'.
    # Esta validador tem a função de gerar um username para o usuário a partir do seu nome,
    # caso o username não tiver sido definido.
    @field_validator("username", mode="before")
    @classmethod
    def generate_username_if_not_set(
        cls, value: str | None, info: ValidationInfo
    ) -> str:
        """Generates username if not set"""
        # Verifica se 'value' (username) não está definido.
        if value is None:
            # Senão estiver definido, gera um username a partir do nome.
            # O objeto 'info' que é do tipo 'ValidationInfo' permite acessar
            # os valores e nomes de outros campos no momento da criação da instância
            # de UserRequest.
            value = generate_username(info.data["name"])
        # Retorna o campo validado, é obrigatório sempre retornar um valor.
        return value

    # Outro validador, mas para o campo 'password' que também vai ser executado antes
    # mesmo de instanciar a classe UserRequest. Também precisa do decorator para ser um
    # método da classe '@classmethod' permitindo receber o contexto da instância.
    # Este validador tem a função de realizar o hash da senha (password) do usuário.
    @field_validator("password", mode="before")
    @classmethod
    def hash_password(cls, value: str) -> str:
        # Retorna o hash sempre ao criar um novo usuário.
        return get_password_hash(value)


# Serializer para validar a operação de PATCH (update parcial) de um usuário.
class UserProfilePatchRequest(BaseModel):
    """Serializer for when client wants to partially update user."""

    # Apenas os campos 'avatar' e 'bio' podem ser alterados.
    avatar: Optional[str] = None
    bio: Optional[str] = None

    # Validação a nível de modelo, 'mode=before' indica que vai ser executada
    # antes da criação da instância.
    # @classmethod indica que é um método da classe, recebendo o contexto 'cls'.
    @model_validator(mode="before")
    @classmethod
    # Validação que garante que pelo menos um campo será passado no update.
    # Caso nenhum campo for passado, invoca uma exceção HTTP do tipo 400,
    # indicando uma requisição inválida.
    def ensure_values(cls, values):
        if not values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bad request, no data informed.",
            )

        # É necessário retornar os valores já validados para que a validação funcione.
        return values
