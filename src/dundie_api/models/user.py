# Classe para definir que uma variável pode ser None, ou seja, opcional.
from typing import Optional, TYPE_CHECKING

# Classes para realizar modelagem de dados.
# 'Field' declara um campo de uma tabela e 'SQLModel' permite que uma classe
# se torne, através de herança, uma representação de uma tabela (modelo de dados).
from sqlmodel import Field, SQLModel, Relationship

# Realiza o import apenas no momento de verificação dos tipos e não em execução para
# evitar circular import.
if TYPE_CHECKING:
    from dundie_api.models.transaction import Transaction, Balance


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
    password: str = Field(nullable=False)
    # Campo para armazenar o nome do usuário, obrigatório. (Not Null)
    name: str = Field(nullable=False)
    # Campo para armazenar o departamento do usuário na empresa, obrigatório. (Not Null)
    dept: str = Field(nullable=False)
    # Campo para armazenar o tipo de moeda que o usuário utiliza (ex: BRL, USD). Também
    # não pode ser Nulo (obrigatório).
    currency: str = Field(nullable=False)

    # Campo que declara a relação entre a tabela 'Transaction' e 'User'. Ele permite acessar
    # todas as transações de entrada de pontos e também define um campo 'user' na tabela
    # 'Transaction' para acessar o usuário que está recebendo a pontuação.
    # 'sa_relationship_kwargs' com 'primaryjoin' define o JOIN a ser realizado entre as
    # duas tabelas, utilizando a chave primária e chave estrangeira.
    incomes: Optional[list["Transaction"]] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"primaryjoin": "User.id == Transaction.user_id"},
    )

    # Campo que declara a relação entre a tabela 'Transaction' e 'User'. Ele permite acessar
    # todas as transações de saída de pontos e também define um campo 'from_user' na tabela
    # 'Transaction' para acessar o usuário que está enviando os pontos.
    # 'sa_relationship_kwargs' com 'primaryjoin' define o JOIN a ser realizado entre as
    # duas tabelas, utilizando a chave primária e chave estrangeira.
    expenses: Optional[list["Transaction"]] = Relationship(
        back_populates="from_user",
        sa_relationship_kwargs={"primaryjoin": "User.id == Transaction.from_id"},
    )

    # Campo que declara a relação entre a tabela 'Balance' e 'User'. Ele permite acessar o
    # saldo do usuário a partir da tabela User e também popula um campo 'user' na tabela
    # 'Balance' para acessar qual o usuário daquele saldo.
    # 'sa_relationship_kwargs' com 'lazy' igual a 'dynamic' define que esse campo não vai
    # ser populado logo de início ao criar a instância, ele só irá realizar a query apenas
    # no momento em que for chamado.
    # Por ter um underline no nome, este atributo não deve ser acessado diretamente, em vez
    # disso, deve-se utilizar a propriedade '.balance'.
    _balance: Optional["Balance"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "dynamic"}
    )

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

    # Decorator para transformar a função em uma propriedade, e esta propriedade
    # tem a função de pegar o saldo do usuário.
    @property
    def balance(self) -> int:
        """Return the current balance of the user"""

        # Definindo a variável 'user_balance' e ao mesmo tempo buscando na tabela 'Balance'
        # através da relação '_balance' para verificar se ele está vazio ou não.
        if (user_balance := self._balance.first()) is not None:  # pyright: ignore
            return user_balance.value

        # Retorna zero se o saldo não estiver definido.
        return 0


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
