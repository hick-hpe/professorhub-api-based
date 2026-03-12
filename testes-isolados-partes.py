class AuthError(Exception):
    """
    Erro base para problemas relacionados à autenticação.
    """

    def __init__(self, message="Erro de autenticação"):
        super().__init__(message)


class TokenInvalidoError(AuthError):
    """
    Token não encontrado ou inválido.
    """

    def __init__(self, message="Token inválido"):
        super().__init__(message)


class TokenExpiradoError(AuthError):
    """
    Token expirado.
    """

    def __init__(self, email=None, message="Token expirado"):
        self.email = email
        super().__init__(message)


class UsuarioNaoEncontradoError(AuthError):
    """
    Usuário não encontrado.
    """

    def __init__(self, message="Usuário não encontrado"):
        super().__init__(message)


class ProfessorNaoEncontradoError(AuthError):
    """
    Professor não encontrado.
    """

    def __init__(self, message="Professor não encontrado"):
        super().__init__(message)


# testes - mini bateria de testes
def testar_exceptions():

    testes = [
        AuthError(),
        TokenInvalidoError(),
        TokenExpiradoError(email="teste@email.com"),
        UsuarioNaoEncontradoError(),
        ProfessorNaoEncontradoError()
    ]

    for erro in testes:
        try:
            raise erro
        except AuthError as e:
            print("\nTipo:", type(e).__name__)
            print("Mensagem:", e)

            if hasattr(e, "email"):
                print("Email:", e.email)


testar_exceptions()