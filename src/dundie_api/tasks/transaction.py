from typing import Optional
from sqlmodel import Session
from dundie_api.db import engine
from dundie_api.models import User, Transaction, Balance


# Definindo uma exceção personalizada para as transações.
class TransactionError(Exception):
    """Can't add transaction"""


# Função para criar uma nova transação entre dois usuários.
# 'user' é o usuário que está recebendo as moedas.
# 'from_user' é o usuário que está enviando as moedas.
# 'value' é o valor da transação.
# 'session' é a sessão de conexão com o banco de dados, sendo opcional.
def add_transaction(
    *,
    user: User,
    from_user: User,
    value: int,
    session: Optional[Session] = None
):
    """Add a new transaction to the specified user.
    
    params:
        user: The user to add transaction to.
        from_user: The user where amount is coming from or superuser
        value: The value being added
    """

    # Cláusula de guarda, se o usuário não for um super usuário e o seu saldo
    # for menor que o valor que ele está tentando transferir, invoca a exceção
    # informando que o saldo é insuficiente.
    if not from_user.superuser and from_user.balance < value:
        raise TransactionError("Insufficient balance")

    # Cria uma nova sessão de banco de dados ou então utiliza a sessão passada
    # no parâmetro.
    session = session or Session(engine)

    # Instância uma nova transação, informando todos os campos necessários.
    transaction = Transaction(user=user, from_user=from_user, value=value) # type: ignore

    # Adiciona a transação a sessão de conexão com o banco de dados.
    session.add(transaction)

    # Adiciona a transação no banco de dados.
    # TODO: Tratar erros.
    session.commit()

    # Consulta o banco de dados e atualiza os dados dos usuário da transação.
    session.refresh(user)
    session.refresh(from_user)

    # Para cada usuário, calcula o total de saídas e entradas de pontos para definir
    # seu saldo.
    for holder in (user, from_user):
        # Soma todos os valores das transações recebidas.
        total_income = sum([t.value for t in holder.incomes]) # type: ignore
        # Soma todos os valores das transações enviadas.
        total_expense = sum([t.value for t in holder.expenses]) # type: ignore

        # Tenta encontrar na tabela 'balance' se o usuário em questão já possui
        # um saldo, caso ele não possuir nenhum saldo definido, instância um novo
        # objeto para definir seu saldo.
        balance = session.get(
            Balance, holder.id
        ) or Balance(user=holder, value=0) # type: ignore

        # Realiza o cálculo do seu novo saldo, subtraindo os gastos dos ganhos totais.
        balance.value = total_income - total_expense

        # Adiciona a sessão de conexão ao banco de dados.
        session.add(balance)

    # Após definir todos os novos saldos de cada um dos usuários, reflete as informações
    # no banco de dados.
    session.commit()
    