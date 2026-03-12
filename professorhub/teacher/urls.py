from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.submit_register_view, name="submit_register"),
    path("login/", views.submit_login_view, name="submit_login"),
    path('logout/', views.logout_view, name='logout'),

    path('enviar-email/', views.enviar_email_verificacao_view, name='enviar_email_verificacao_view'),
    path('reenviar-email/', views.reenviar_email_verificacao_view, name='reenviar_email_verificacao'),
    path('ativar-conta/', views.ativar_conta_view, name='ativar_conta_view'),
    path('recuperar-senha/', views.recuperar_senha_view, name='recuperar_senha'),
    path('validar-codigo/', views.validar_codigo_recuperacao_senha_view, name='validar_codigo'),
    path('redefinir-senha/', views.redefinir_senha_view, name='redefinir_senha'),
    path("enviar-contato/", views.enviar_email_form_contato_view, name="enviar_email_form_contato"),
]
# palermohpe@gmail.com