from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from planner.models import Professor, TokenAtivacaoConta
import secrets
from teacher.errors.exceptions import (
    AuthError,
    UsuarioNaoEncontradoError,
    ProfessorNaoEncontradoError,
    TokenInvalidoError,
    TokenExpiradoError
)

# padronizar os erros/return dos services
# app/errors/exceptions.py


def fazer_login_usuario(email, senha):
    """
    Valida credenciais e retorna usuário autenticado.
    """

    if not email or not senha:
        raise AuthError("Preencha todos os campos!")

    user = User.objects.filter(email=email).first()

    if not user:
        raise UsuarioNaoEncontradoError()

    user = authenticate(username=user.username, password=senha)

    if not user:
        raise AuthError("Credenciais inválidas. Verifique e tente novamente!")

    return user


def registrar_usuario(nome, email, senha, confirm_senha):
    """
    Valida credenciais e retorna usuário cadastrado/autenticado.
    """

    if not nome or not email or not senha or not confirm_senha:
        raise AuthError("Algum campo está vazio.")

    if User.objects.filter(email=email).exists():
        raise AuthError("Email já cadastrado. Escolha outro ou tente fazer o login.")

    if senha != confirm_senha:
        raise AuthError("As senhas não coincidem.")

    if len(senha) < 8:
        raise AuthError("A senha deve ter no mínimo 8 caracteres.")

    try:

        user = User.objects.create_user(
            username=nome,
            email=email,
            password=senha,
            first_name=nome
        )

        # cria professor
        professor = Professor.objects.create(user=user)

        # cria token de ativação
        TokenAtivacaoConta.objects.create(
            professor=professor,
            token=secrets.token_urlsafe(32),
        )

        user = authenticate(username=nome, password=senha)

        if not user:
            raise AuthError("Usuário criado, mas falha ao autenticar.")

        return user

    except Exception as e:
        raise AuthError(f"Erro ao criar usuário: {e}")


def atualizar_token(token_obj):
    professor = token_obj.professor

    token_obj.delete()

    novo_token = secrets.token_urlsafe(32)

    TokenAtivacaoConta.objects.create(
        professor=professor,
        token=novo_token
    )


def ativar_conta_por_token(token):
    if not token:
        raise TokenInvalidoError()

    try:
        token_obj = TokenAtivacaoConta.objects.get(token=token)
    except TokenAtivacaoConta.DoesNotExist:
        raise TokenInvalidoError()

    email = token_obj.professor.user.email 

    if token_obj.codigo_expirou():
        atualizar_token(token_obj)
        raise TokenExpiradoError(email)

    user = User.objects.filter(email=email).first()

    if not user:
        raise UsuarioNaoEncontradoError()

    professor = Professor.objects.filter(user=user).first()

    if not professor:
        raise ProfessorNaoEncontradoError()

    professor.conta_ativada = True
    professor.save()

    token_obj.delete()

    return professor


