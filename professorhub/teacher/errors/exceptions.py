class AuthError(Exception):
    """
    Erro base para problemas relacionados à autenticação.
    """

    def __init__(self, message="Erro de autenticação"):
        super().__init__(message)


class UsuarioNaoEncontradoError(AuthError):
    """
    Usuário não encontrado.
    """

    def __init__(self, message="Usuário não encontrado"):
        super().__init__(message)


class ProfessorNaoEncontradoError(UsuarioNaoEncontradoError):
    """
    Professor não encontrado.
    """

    def __init__(self, message="Professor não encontrado"):
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

