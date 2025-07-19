# Biblioteca para criar interfaces de linha de comando.
import typer

# Biblioteca para estilizar interfaces de linha de comando.
from rich.console import Console
from rich.table import Table

# Biblioteca para manipular banco de dados.
from sqlmodel import Session, select

# Importando as configurações, engine e model User do app.
from .config import settings
from .db import engine
from .models import User

# Instanciando a classe do Typer, a instância é responsável por
# criar todos os comandos.
# Define o nome da CLI usando 'name' e faz com que o autocomplete não
# seja usado com 'add_completion'.
main = typer.Typer(name="dundie CLI", add_completion=False)


# Mapeia um comando a ser exibido na CLI. Todo comando Typer deve estar
# atribuído a uma função. A ação de função é de abrir um shell iterativo
# com todos os imports necessários para manipular o app.
# O nome da função vira o nome do comando.
@main.command()
def shell():
    """Opens interactive shell"""

    # Variáveis a serem passadas para o shell interativo.
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
    }
    # Imprime uma mensagem no console informando os módulos que
    # foram importados automaticamente.
    typer.echo(f"Auto imports: {list(_vars.keys())}")

    # Tenta importar e iniciar um shell do ipython, caso o ipython não
    # esteja disponível no ambiente, ele invoca o shell padrão do Python.
    try:
        # Tenta importar o ipython
        from IPython import start_ipython

        # Função responsável por abrir um shell interativo do ipython. O
        # parâmetro 'argv' é responsável por passar argumentos para a
        # inicialização do shell e 'user_ns' passa as variáveis que vão ser
        # iniciadas juntas com o ipython, tornando-as disponíveis dentro do shell.
        start_ipython(argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars)
    except ImportError:
        # Importa a biblioteca padrão para emular o shell padrão do Python.
        import code

        # Invoca o shell padrão do Python com 'InteractiveConsole' passando as variáveis para ficarem
        # disponíveis para execução e 'interact' é uma função para incializar um loop de read-eval-print.
        code.InteractiveConsole(_vars).interact()


# Mapeia outro comando para ser exibido na interface do Typer. A ação desse comando é de
# listar todos os usuários cadastrados no banco de dados.
# O nome do comando passa a ser 'user-list', o underline (_) é alterado para um traço.
@main.command()
def user_list():
    """Lists all users"""

    # Cria uma tabela estilizada com o título "dundie users".
    table = Table(title="dundie users")
    # Lista de campos que vão ser as colunas da tabela.
    fields = ["name", "username", "dept", "email", "currency"]
    # Para cada campo na lista, adiciona uma coluna na tabela com
    # o nome contido na lista de campos e atribui a cor magenta a todas.
    for header in fields:
        table.add_column(header, style="magenta")

    # Abre um gerenciador de contextos com uma sessão do banco de dados,
    # permitindo a execução de querys SQL.
    with Session(engine) as session:
        # Executa uma query (exec) para selecionar (select) todos os usuários
        # no banco de dados (User) e armazena em uma variável.
        users = session.exec(select(User))

        # Para cada usuário cadastrado no banco de dados adiciona uma linha na
        # tabela para exibir todos os seus dados (desempacotamento com 'getattr',
        # percorrendo todos os campos usando list comprehension).
        for user in users:
            table.add_row(*[getattr(user, field) for field in fields])

    # Imprime a tabela estilizada no terminal.
    Console().print(table)
