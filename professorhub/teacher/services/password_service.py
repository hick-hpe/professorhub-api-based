from django.contrib.auth.models import User
from planner.models import CodigoRecuperacaoSenha
import random
from teacher.errors.exceptions import UsuarioNaoEncontradoError
from .email_service import enviar_email_para_recuperar_conta


# tirar daqui (utils?? -> (utils.py))
def gerar_codigo():
    """Gerar código de recuperação de senha"""
    return f"{random.randint(0,999999):06d}"


def iniciar_recuperacao_conta(email):

    if not email:
        raise ValueError("Email não informado")

    user = User.objects.filter(email=email).first()

    if not user:
        raise UsuarioNaoEncontradoError("Nenhuma conta foi encontrada com esse email.")

    # gerar código
    codigo = gerar_codigo()

    # salvar código
    CodigoRecuperacaoSenha.objects.create(
        email=email,
        code=codigo
    )

    # enviar email
    enviar_email_para_recuperar_conta(email, codigo)

    return True

