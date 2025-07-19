"""Settings module"""
# Biblioteca para manipular rotinas do Sistema Operacional.
import os
# Biblioteca para configuração.
from dynaconf import Dynaconf, Validator # type: ignore

# Armazena o caminho absoluto deste arquivo.
HERE = os.path.dirname(os.path.abspath(__file__))

# Declarando a variável de configurações, através dela vai ser possível
# importar acessar as variáveis de ambiente ou de arquivos.
settings = Dynaconf(
    # Definindo o prefixo para as variáveis de ambiente, apenas variáveis de
    # ambiente com este prefixo (em maiúsculo) vão ser lidas.
    envvar_prefix="dundie",
    # Indica o arquivo que configuração padrão que vai ser carregado
    # automaticamente pela aplicação.
    preload=[os.path.join(HERE, "default.toml")],
    # Indica outros arquivos que podem conter configurações necessárias.
    settings_files=["settings.toml", ".secrets.toml"],
    # Define múltiplos ambientes, podendo separar configurações para diferentes
    # situações, como de produção ou desenvolvimento.
    environments=["development", "production", "testing"],
    # Define a variável de ambiente 'dundie_env' como a variável responsável
    # por alterar qual ambiente vai usar.
    env_switcher="dundie_env",
    # Impede o carregamento de variáveis de ambiente de um arquivo .env
    # se for True, a biblioteca vai tentar importar deste arquivo.
    load_dotenv=False,
    # Lista de validadores para realizar validações em cima de variáveis de configuração.
    validators=[
        # Validador que verifica se a chave 'SECRET_KEY' existe dentro da sessão
        # 'SECURITY' dentro dos arquivos de configuração ou nas variáveis de ambiente.
        # Ele também define que essa chave deve ser do tipo string e seu tamanho mínimo
        # deve ser de 64 caracteres.
        Validator("SECURITY__SECRET_KEY", must_exist=True, is_type_of=str, len_min=64)
    ]
)