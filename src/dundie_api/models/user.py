# Classe para definir que uma variável pode ser None, ou seja, opcional.
from typing import Optional

# Classes para realizar modelagem de dados.
# 'Field' declara um campo de uma tabela e 'SQLModel' permite que uma classe
# se torne, através de herança, uma representação de uma tabela (modelo de dados).
from sqlmodel import Field, SQLModel


# Criando a classe 'User', que representa a tabela 'user' no banco de dados.
# Através dessa classe é possível modelar e manipular essa tabela. Representa
# o modelo da tabela 'user'.
class User(SQLModel, table=True):
    """Represents the User Model"""

    # Campo que indica o ID (chave primária), ele é opcional pois
    # só vai ser preenchido ao ser enviado ao banco de dados.
    # Este campo representa cada instância de usuário.
    id: Optional[int] = Field(default=None, primary_key=True)
    # Campo para armazenar o email do usuário, não pode se repetir e não pode ser Nulo.
    email: str = Field(unique=True, nullable=False)
    # Campo para armazenar o username do usuário, tendo que ser único na tabela
    # toda e não pode ser Nulo.
    username: str = Field(unique=True, nullable=False)
    # Campo para incluir o URL do avatar do usuário, ele é opcional, mas podendo
    # ser uma string.
    avatar: Optional[str] = None
    # Campo para a biografia do usuário, também é opcional, mas pode ser uma string.
    bio: Optional[str] = None
    # Campo para armazenar a senha do usuário, sendo um campo obrigatório.
    hashed_password: str = Field(nullable=False)
    # Campo para armazenar o nome do usuário, obrigatório. (Not Null)
    name: str = Field(nullable=False)
    # Campo para armazenar o departamento do usuário na empresa, obrigatório. (Not Null)
    dept: str = Field(nullable=False)
    # Campo para armazenar o tipo de moeda que o usuário utiliza (ex: BRL, USD). Também
    # não pode ser Nulo (obrigatório).
    currency: str = Field(nullable=False)

    # Decorator para transformar um método em uma propriedade, dessa forma,
    # ele pode ser chamado como uma propriedade da classe, sem a necessidade
    # de chamar o método como uma função.
    # Uma propriedade é um atributo de classe que é calculado dinamicamente, em
    # vez de ser armazenado em memória.
    @property
    # Função que retorna se o usuário é um admin ou não. Para ser admin basta
    # ter o departamento igual a "Management (Gerência)
    def superuser(self):
        """Users belonging to Management dept are admins."""
        return self.dept == "management"


# TODO: Use slugify library
# TODO: Move to UserRequest
# Função para gerar um username a partir do nome do usuário (slug).
def generate_username(name: str) -> str:
    """Generate a slug from user.name.
    >>> "Bruno Rocha" -> "bruno-rocha"
    """

    # Converte tudo para minúsculo e substituí os espaços em branco
    # por traços (-).
    return name.lower().replace(" ", "-")
