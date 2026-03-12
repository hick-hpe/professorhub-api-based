from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from planner.models import Professor, TokenAtivacaoConta
import secrets


def fazer_login_usuario(email, senha):
    """
    Valida credenciais e retorna usuário autenticado ou erro.
    """

    if not email or not senha:
        return None, "Preencha todos os campos."

    user = User.objects.filter(email=email).first()

    if user is None:
        return None, "Usuário não cadastrado."

    user = authenticate(username=user.username, password=senha)

    if user is None:
        return None, "Credenciais inválidas. Verifique e tente novamente."

    return user, None



def registrar_usuario(nome, email, senha, confirm_senha):

    if not nome or not email or not senha or not confirm_senha:
        return None, "Algum campo está vazio."

    if User.objects.filter(email=email).exists():
        return None, "Email já cadastrado. Escolha outro ou tente fazer o login."

    if senha != confirm_senha:
        return None, "As senhas não coincidem."

    if len(senha) < 8:
        return None, "A senha deve ter no mínimo 8 caracteres."

    try:

        user = User.objects.create_user(
            username=nome,
            email=email,
            password=senha,
            first_name=nome
        )

        # cria token de ativação
        TokenAtivacaoConta.objects.create(
            email=user.email,
            token=secrets.token_urlsafe(32),
        )

        # cria professor
        Professor.objects.create(user=user)

        # autentica usuário
        user = authenticate(username=nome, password=senha)

        if not user:
            return None, "Usuário criado, mas falha ao autenticar."

        return user, None

    except Exception as e:
        return None, f"Erro ao criar usuário: {e}"


