"""Security utilities"""

# TODO: Use scrypt or argon2

# Biblioteca para criar e verificar hashes de senhas usando múltiplos algoritmos.
from passlib.context import CryptContext

# Criando um contexto, que vai ser usado para criar e vericiar os hashes
# 'schemes' declara quais os algoritmos vão ser usados para criar os hashes e
# 'deprecated' como 'auto' define que todos os algoritmos, tirando o padrão, vão ser
# considerads depreciados.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Função para verificar se a senha inserida é igual ao hash armazenado no banco de dados.
# Retorna um booleano indicando se é (True) ou não (False) igual.
def verify_password(plain_password, hashed_password) -> bool:
    """Verifies a hash against a password"""
    return pwd_context.verify(plain_password, hashed_password)


# Função para criar o hash a partir da senha do usuário.
# Retorna a string contendo o hash.
def get_password_hash(password) -> str:
    """Generate a hash from plain text"""
    return pwd_context.hash(password)


# Estendendo o tipo str criando a própria classe para validar e criar
# as hashes no modelo do SQLModel usando Pydantic.
class HashedPassword(str):
    """Takes a plain text password and hashes it.
    use this as a field in your SQLModel
    class User(SQLModel, table=True):
        username: str
        password: HashedPassword
    """

    # Criando um método da classe que vai invocar todos as funções validadoras,
    # definidas na classe, dessa forma ao usar essa classe como Type Annotation
    # no model do SQLModel, esses validadores vão ser invocados.
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    # Método de classe para criar a hash da senha do usuário.
    @classmethod
    def validate(cls, v):
        """Accepts a plain text password and returns a hashed password."""
        # Verifica se o tipo de dado inserido é uma string, senão for, retorna um erro.
        if not isinstance(v, str):
            raise TypeError("string required")

        # Cria o hash da senha 'v' usando a função e algoritmos definidos
        # anteriormente.
        hashed_password = get_password_hash(v)

        # Retorna o hash da senha, este valor que vai atribuído na variável que
        # receber esta classe como Type Annotation
        return cls(hashed_password)
