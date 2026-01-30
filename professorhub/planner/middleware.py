from django.shortcuts import redirect
from django.urls import reverse
from planner.models import Professor

class ContaAtivadaMiddleware:
    """
    Bloqueia o acesso de usuários logados que não têm conta ativada.
    Usuários com conta ativada continuam para a rota desejada.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Rotas públicas que não exigem conta ativada
        rotas_livres = [
            reverse('submit_login'),
            reverse('submit_register'),
            reverse('enviar_email_verificacao_view'),
            reverse('reenviar_email_verificacao'),
            reverse('conta_ativada_view'),
            reverse('recuperar_senha'),
            reverse('validar_codigo'),
            reverse('redefinir_senha'),
            '/admin/',
            '/static/',
            '/media/'
        ]

        # se for a index
        if request.path == '/':
            return self.get_response(request)

        if any(request.path.startswith(r) for r in rotas_livres):
            print('ok')
            return self.get_response(request)

        # Se usuário não está autenticado, deixa seguir
        if not request.user.is_authenticated:
            return redirect('index')

        # Verifica se a conta está ativada
        professor = Professor.objects.filter(user=request.user).first()
        if not professor:
            return redirect('enviar_email_verificacao_view')

        if not professor.conta_ativada:
            return redirect('enviar_email_verificacao_view')

        # Se chegou até aqui, a conta está ativada → deixa continuar
        return self.get_response(request)

