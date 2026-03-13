import secrets
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from planner.models import Professor, CodigoRecuperacaoSenha, TokenAtivacaoConta
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.db import transaction
import datetime
from .services.auth_service import (
    fazer_login_usuario,
    registrar_usuario,
    ativar_conta_por_token,
)
from .services.password_service import iniciar_recuperacao_conta
from teacher.errors.exceptions import (
    AuthError,
    UsuarioNaoEncontradoError,
    TokenExpiradoError,
    ProfessorNaoEncontradoError,
    TokenInvalidoError,
)


def submit_login_view(request):

    if request.method == 'POST':

        email = request.POST.get('loginEmail')
        senha = request.POST.get('loginPassword')

        try:

            user = fazer_login_usuario(email, senha)

            login(request, user)

            return redirect('admin_dashboard')

        except AuthError as e:

            messages.error(request, str(e))
            return redirect("submit_login")

    return render(request, 'teacher/login.html')


def submit_register_view(request):

    if request.method == 'POST':

        nome = request.POST.get('registerName')
        senha = request.POST.get('registerPassword')
        confirm_senha = request.POST.get('confirmPassword')
        email = request.POST.get('registerEmail')

        try:

            user = registrar_usuario(nome, email, senha, confirm_senha)

            login(request, user)

            try:
                enviar_email_para_ativar_conta(request)
            except Exception as e:
                print("(submit_register) Erro ao enviar email de ativação de conta:", e)

            return redirect('enviar_email_verificacao_view')

        except AuthError as e:

            messages.error(request, str(e))
            return redirect('submit_register')

    return render(request, 'teacher/register.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu da sua conta com sucesso.")
    return redirect('index') 


@login_required(login_url='index')
def enviar_email_verificacao_view(request):
    """
    Exibe a página avisando o usuário para verificar o e-mail
    """
    return render(request, 'teacher/ativar_conta.html', {'user': request.user})


@transaction.atomic
def ativar_conta_view(request):

    token = request.GET.get("token")

    try:

        professor = ativar_conta_por_token(token)

        return render(request, "teacher/conta_ativada.html", {
            "professor": professor
        })

    except TokenExpiradoError as e:
        return render(request, "teacher/erro_token.html", {
            "tipo_erro": "Token expirado",
            "email": e.email
        })

    except TokenInvalidoError:
        return render(request, "teacher/erro_token.html", {
            "tipo_erro": "Token inválido ou inexistente",
            "token": token
        })

    except UsuarioNaoEncontradoError:
        return HttpResponse("Usuário não encontrado.", status=404)

    except ProfessorNaoEncontradoError:
        return HttpResponse("Professor não encontrado.", status=404)


def enviar_email_para_ativar_conta(request):
    # Cria o link para ativação
    link_base = request.build_absolute_uri(reverse('ativar_conta_view'))
    professor = get_object_or_404(Professor, user=request.user)
    token = get_object_or_404(TokenAtivacaoConta, professor=professor).token
    link_ativacao = f'{link_base}?token={token}'

    # dados do email
    subject = 'Ative sua conta'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [request.user.email]

    text_content = f'Quase lá! Clique no link para ativar sua conta: {link_ativacao}'
    html_content = f"""
        <div style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 30px;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <tr>
                <td style="background-color: #3f61c7; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0;">Quase lá!</h1>
                </td>
            </tr>
            <tr>
                <td style="padding: 30px;">
                    <p style="font-size: 16px; color: #333;">Olá,</p>
                    <p style="font-size: 16px; color: #333; line-height: 1.5;">
                        Você está a um passo de ativar sua conta. Clique no botão abaixo para concluir o processo:
                    </p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{link_ativacao}" 
                        style="background-color: #3f61c7; color: white; text-decoration: none; padding: 12px 25px; font-size: 16px; border-radius: 5px; display: inline-block;">
                            Ativar Conta
                        </a>
                    </p>
                    <p style="font-size: 14px; color: #777; line-height: 1.5;">
                        Se o botão não funcionar, copie e cole o link abaixo no seu navegador:<br>
                        <a href="{link_ativacao}" style="color: #3f61c7;">{link_ativacao}</a>
                    </p>
                    <p style="font-size: 14px; color: #777; text-align: center; margin-top: 40px;">
                        &copy; {datetime.date.today().year} ProfessorHub. Todos os direitos reservados.
                    </p>
                </td>
            </tr>
        </table>
    </div>
    """

    # enviar
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


@login_required(login_url='index')
def reenviar_email_verificacao_view(request):
    # reenviar email de ativação para o usuário
    user = request.user
    professor = Professor.objects.filter(user=user).first()
    if not professor:
        return redirect('index')

    enviar_email_para_ativar_conta(request)

    return redirect('enviar_email_verificacao_view')


def recuperar_senha_view(request):

    # zerar etapas
    request.session['page_recuperar_senha'] = False
    request.session['page_validar_codigo'] = False
    
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            iniciar_recuperacao_conta(email)

            # salva sessão
            request.session['email_recuperacao'] = email
            request.session['page_recuperar_senha'] = True

            messages.success(request, 'Um código de recuperação foi enviado para o seu email.')

            return redirect('validar_codigo')

        except UsuarioNaoEncontradoError as e:

            messages.error(request, str(e))

    return render(request, 'teacher/recuperar-senha.html')


def validar_codigo_recuperacao_senha_view(request):
    # se passsou pela etapa anterior, continua
    etapa_recuperar_senha = request.session.get('page_recuperar_senha')
    print('--- Validar código ---')
    print('etapa_recuperar_senha:',etapa_recuperar_senha)
    if not etapa_recuperar_senha:
        return redirect('recuperar_senha')
    
    # validar o código para permitir redefinição de senha
    if request.method == 'POST':

        email = request.session.get('email_recuperacao')
        codigo = request.POST.get('codigo')

        # verifica se existe o código associado àquele email
        professor = Professor.objects.filter(
            user__email=email
        ).first()
        if not professor:
            raise ProfessorNaoEncontradoError()
            
        codigo_obj = CodigoRecuperacaoSenha.objects.filter(professor=professor, code=codigo)
        if codigo_obj.exists():
            codigo_obj = codigo_obj.first()
            if not codigo_obj.codigo_expirou():
                codigo_obj.delete()
                messages.success(request, 'Código validado com sucesso. Agora redefina sua senha.')
                # salvar etapa
                request.session['page_validar_codigo'] = True

                return redirect('redefinir_senha')
            else:
                messages.error(request, 'Código expirado. Tente novamente.')
        else:
            messages.error(request, 'Código inválido. Tente novamente.')

    return render(request, 'teacher/validar-codigo.html')


def redefinir_senha_view(request):
    etapa_recuperar_senha = request.session.get('page_recuperar_senha')
    etapa_validar_codigo = request.session.get('page_validar_codigo')
    print('--- Redefinir Senha ---')
    print('etapa_recuperar_senha:',etapa_recuperar_senha)
    print('etapa_validar_codigo:',etapa_validar_codigo)
    if not (etapa_recuperar_senha and etapa_validar_codigo):
        return redirect('recuperar_senha')
        
    if request.method == 'POST':
        senha = request.POST.get('senha')
        confirm_senha = request.POST.get('confirm_senha')

        if senha and confirm_senha:
            if senha == confirm_senha:
                email = request.COOKIES.get('email')
                user = User.objects.filter(email=email).first()

                if not user:
                    messages.error(request, "Usuário não encontrado.")
                    return redirect('submit_login')
                
                user.set_password(senha)
                user.save()

                # excluir 'checkpoints' das etapas
                request.session['email_recuperacao'] = None
                request.session['page_validar_codigo'] = False
                request.session['page_recuperar_senha'] = False

                return redirect('submit_login')
            else:
                messages.error(request, 'As senhas não coindizem')
        else:
            messages.error(request, 'Algum campo está vazio')

    return render(request, 'teacher/redefinir-senha.html')


def enviar_email_form_contato_view(request):
    # enviar email de contato, feedback
    if request.method == "POST":
        nome = request.POST.get("nome")
        email_usuario = request.POST.get("email")
        mensagem = request.POST.get("mensagem")

        # dados para enviar email para o admin
        assunto_admin = f"Contato ProfessorHub - {nome}"
        corpo_admin = (
            f"Nova mensagem recebida:\n\n"
            f"Nome: {nome}\n"
            f"Email: {email_usuario}\n\n"
            f"Mensagem:\n{mensagem}"
        )

        # dados para enviar email para o usuário, informando que enviou a mensagem
        assunto_user = "Recebemos sua mensagem - ProfessorHub"
        corpo_user = (
            f"Olá {nome},\n\n"
            f"Recebemos sua mensagem e em breve nossa equipe entrará em contato.\n\n"
            f"Resumo da sua mensagem:\n{mensagem}\n\n"
            f"Atenciosamente,\nEquipe ProfessorHub"
        )

        # enviar email
        try:
            print("Enviando email para o administrador...")
            send_mail(
                subject=assunto_admin,
                message=corpo_admin,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            print("Email para administrador enviado com sucesso!")

            print("Enviando email de confirmação para o usuário...")
            send_mail(
                subject=assunto_user,
                message=corpo_user,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email_usuario],
                fail_silently=False,
            )
            print("Email de confirmação enviado com sucesso!")

            messages.success(request, "Mensagem enviada com sucesso! Verifique seu e-mail para a confirmação.")
        except Exception as e:
            print("Erro ao enviar email de ativação de conta:", e)
            messages.error(request, f"Ocorreu um erro ao enviar o email: {e}")

        return redirect("index")

    return redirect("index")
