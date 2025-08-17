import smtplib
from datetime import timedelta
from time import sleep

from sqlmodel import Session, select

from dundie_api.auth import create_access_token
from dundie_api.config import settings
from dundie_api.db import engine
from dundie_api.models.user import User


# Função 'proxy' para definir qual processo de envio de e-mail vai
# ser feito. Se a aplicação estiver em modo de debug o e-mail vai
# ser escrito em um arquivo. Senão estiver, ele vai ser enviado de
# fato.
def send_email(email: str, message: str):
    if settings.email.debug_mode is True:  # type: ignore
        _send_email_debug(email, message)
    else:
        _send_email_smtp(email, message)


# Função para simular o envio de e-mails, gravando-os em um arquivo de log
# apenas para teste.
def _send_email_debug(email: str, message: str):
    """Mock email sending by printing to a file"""
    with open("email.log", "a") as f:
        sleep(3)
        f.write(f"--- START EMAIL {email} ---\n{message}\n--- END OF EMAIL ---\n")


# Função que de fato vai abrir uma conexão do tipo SMTP, que é o protocolo
# de envio de e-mail e enviá-lo a um e-mail válido.
def _send_email_smtp(email: str, message: str):
    """Connect to SMTP server and send email"""

    # Criando um servidor SMTP para envio de emails. É preciso passar
    # um 'host' e uma 'porta' de conexão.
    with smtplib.SMTP_SSL(
        settings.email.smtp_server,  # type: ignore
        settings.email.smtp_port,  # type: ignore
    ) as server:
        
        # Realiza a autenticação no servidor de email, caso for necessário, para isso
        # é preciso de um usuário e senha.
        server.login(settings.email.smtp_user, settings.email.smtp_password)  # type: ignore

        # Envio o email de fato, definindo quem vai enviar (sender), quem vai receber
        # (email) e a mensagem que vai ser enviada 'message' codificada em utf-8.
        server.sendmail(
            settings.email.smtp_sender,  # type: ignore
            email,
            message.encode(),
        )


# Template mínimo da mensagem.
MESSAGE = """\
From: Dundie <{sender}>
To: {to}
Subject: Password reset for Dundie

Please use the following link to reset your password:
{url}?pwd_reset_token={pwd_reset_token}

This link will expire in {expire} minutes.
"""


# Função que vai enviar um email para o usuário alterar a senha, caso ele
# seja encontrado na base de dados.
def try_to_send_pwd_reset_email(email):
    """Given an email address send email if user is found"""

    # Abre uma sessão de conexão com o banco de dados
    with Session(engine) as session:

        # Busca o usuário na base de dados, pesquisando pelo email.
        user = session.exec(select(User).where(User.email == email)).first()
        # Caso não encontrar o usuário, encerra o processo.
        if not user:
            return

        # Coleta o remetente (sender), a 'url' do frontend para redicionar o
        # usuário a página de alteração de senha e o tempo de expiração do token
        # (expire) em minutos. Tudo isso vem do arquivo de configurações.
        sender = settings.email.smtp_sender  # type: ignore
        url = settings.security.PWD_RESET_URL  # type: ignore
        expire = settings.security.RESET_TOKEN_EXPIRE_MINUTES  # type: ignore

        # Criando um token para alterar a senha do usuário, definindo o seu
        # 'username' para identificar o token, o tempo de expiração dele 'expires_delta'
        # e o escopo 'scope'.
        pwd_reset_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=expire),  # type: ignore
            scope="pwd_reset",
        )

        # Chamando a função "proxy" para de fato enviar o email dependendo do ambiente.
        # Para isso é passado o email do destinatário e o template da mensagem com
        # todas as informações alteradas.
        send_email(
            email=user.email,
            message=MESSAGE.format(
                sender=sender,
                to=user.email,
                url=url,
                pwd_reset_token=pwd_reset_token,
                expire=expire,
            ),
        )
