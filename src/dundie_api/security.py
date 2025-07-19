"""Security utilities"""

# Biblioteca para criar e verificar hashes de senhas usando o algoritmo Argon2id.
from argon2 import PasswordHasher

# Criando um contexto, que vai ser usado para criar e vericiar os hashes
# 'schemes' declara quais os algoritmos vão ser usados para criar os hashes e
# 'deprecated' como 'auto' define que todos os algoritmos, tirando o padrão, vão ser
# considerads depreciados.
pwd_context = PasswordHasher()


# Função para verificar se a senha inserida é igual ao hash armazenado no banco de dados.
# Retorna um booleano indicando se é (True) ou não (False) igual.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a hash against a password"""
    return pwd_context.verify(hashed_password, plain_password)


# Função para criar o hash a partir da senha do usuário.
# Retorna a string contendo o hash.
def get_password_hash(password: str) -> str:
    """Generate a hash from plain text"""
    return pwd_context.hash(password)


# Função que verifica se o hash está desatualizado ou não para que possa
# ser gerado um novo hash atualizado para a senha do usuário.
def check_needs_rehash(hash: str) -> bool:
    return pwd_context.check_needs_rehash(hash)
