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
import datetime
import random
from .services.auth_service import fazer_login_usuario, registrar_usuario


def submit_login(request):

    if request.method == 'POST':

        email = request.POST.get('loginEmail')
        senha = request.POST.get('loginPassword')

        user, msg_erro = fazer_login_usuario(email, senha)

        if msg_erro:
            messages.error(msg_erro)
            return redirect('submit_login')

        login(request, user)
        return redirect('admin_dashboard')

    return render(request, 'teacher/login.html')


def submit_register(request):

    if request.method == 'POST':

        nome = request.POST.get('registerName')
        senha = request.POST.get('registerPassword')
        confirm_senha = request.POST.get('confirmPassword')
        email = request.POST.get('registerEmail')

        user, msg_erro = registrar_usuario(nome, email, senha, confirm_senha)

        if msg_erro:
            messages.error(request, msg_erro)
            return redirect('submit_register')

        login(request, user)

        try:
            enviar_email_para_ativar_conta(request)
        except Exception as e:
            print("Erro ao enviar email:", e)

        return redirect('enviar_email_verificacao_view')

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


def conta_ativada_view(request):
    """
    Ativa a conta do usuário usando o token enviado por URL.
    Exemplo: /ativar-conta/?token=abcd123
    """

    print("\n=== DEBUG conta_ativada_view ===")

    # capturar token da URL
    token = request.GET.get('token')
    print("Token recebido:", token)

    if not token:
        print("Nenhum token enviado.")
        return HttpResponse("Token inválido ou ausente.", status=400)

    # buscar o token no banco
    try:
        token_obj = TokenAtivacaoConta.objects.get(token=token)
        print("Token encontrado no banco:", token_obj)
    except TokenAtivacaoConta.DoesNotExist:
        print("Token não encontrado.")
        return HttpResponse("Token inválido ou expirado.", status=400)
    
    # tratar expiração/desativação do token
    if token_obj.codigo_expirou():
        # obter o email do token expirado
        email = token_obj.email

        # apagar token expirado
        token_obj.delete()
        print("Token expirado e deletado.")

        # gerar novo token
        novo_token = secrets.token_urlsafe(32)
        TokenAtivacaoConta.objects.create(
            email=email,
            token=novo_token,
        )
        print("Novo token gerado:", novo_token)

        # informa que o token expirou
        return render(request, "teacher/token_expirado.html", {
            "email": email
        })

    # buscar o usuário associado
    email = token_obj.email
    print("Email associado ao token:", email)

    user = User.objects.filter(email=email).first()
    print("Usuário encontrado:", user)

    if not user:
        print("Nenhum usuário encontrado para este token.")
        return HttpResponse("Token inválido. Usuário não encontrado.", status=400)

    # buscar professor
    professor = Professor.objects.filter(user=user).first()
    print("Professor encontrado:", professor)

    if not professor:
        print("Professor não encontrado.")
        return HttpResponse("Usuário não é um professor.", status=400)

    # ativar conta
    professor.conta_ativada = True
    professor.save()
    print("Conta ativada com sucesso:", professor.conta_ativada)

    # remover token
    token_obj.delete()
    print("Token deletado!")

    print("Renderizando página conta_ativada.html\n")
    return render(request, 'teacher/conta_ativada.html')


def enviar_email_para_ativar_conta(request):
    # Cria o link para ativação
    link_base = request.build_absolute_uri(reverse('conta_ativada_view'))
    token = get_object_or_404(TokenAtivacaoConta, email=request.user.email).token
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


def enviar_email_para_recuperar_senha(email, codigo):
    print("1 - Entrou na função")

    try:
        # dados do email
        subject = 'Redefinição de senha'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]
        data = datetime.date.today().year

        print("2 - Dados básicos definidos")

        text_content = f'Quase lá!'
        html_content = f"""
            <div style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 30px;">
                <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background-color: #1C6EA4; padding: 20px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0;">Redefinição de senha</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px;">
                            <p style="font-size: 16px; color: #333;">Olá,</p>
                            <p style="font-size: 16px; color: #333; line-height: 1.5;">
                                Você solicitou uma redefinição de senha. Seu código de verificação é:
                            </p>
                            <p style="text-align: center; margin: 30px 0; font-size: 30px; font-weight: bold; letter-spacing: 2px;">
                                {codigo}
                            </p>
                            <p style="font-size: 14px; color: #777; text-align: center; margin-top: 40px;">
                                &copy; {data} ProfessorHub. Todos os direitos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </div>
        """

        print("3 - HTML criado")

        # criar email
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)

        print("4 - Objeto de email criado")

        msg.attach_alternative(html_content, "text/html")
        
        print("5 - HTML anexado")

        # enviar email
        msg.send(fail_silently=False)

        print("6 - Email enviado com sucesso")

    except Exception as e:
        print("ERRO AO ENVIAR EMAIL:", e)


@login_required(login_url='index')
def reenviar_email_verificacao(request):
    # reenviar email de ativação para o usuário
    user = request.user
    professor = Professor.objects.filter(user=user).first()
    if not professor:
        return redirect('index')

    enviar_email_para_ativar_conta(request)

    return redirect('enviar_email_verificacao_view')


def gerar_codigo():
    # gerar código de recuperação de senha
    return f"{random.randint(0,999999):06d}"


def recuperar_senha_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            # salva o email nos cookies
            response = redirect('validar_codigo')
            request.session['email_recuperacao'] = email

            # gera e salva código no banco
            codigo = gerar_codigo()
            CodigoRecuperacaoSenha.objects.create(email=email, code=codigo)

            # envia o email
            enviar_email_para_recuperar_senha(email, codigo)

            messages.success(request, 'Um código de recuperação foi enviado para o seu email.')
            return response
        else:
            messages.error(request, 'Nenhuma conta foi encontrada com esse email.')

    return render(request, 'teacher/recuperar-senha.html')


def validar_codigo_recuperacao_senha_view(request):
    # validar o código para permitir redefinição de senha
    if request.method == 'POST':
        email = request.session.get('email_recuperacao')
        codigo = request.POST.get('codigo')

        # verifica se existe o código associado àquele email
        codigo_obj = CodigoRecuperacaoSenha.objects.filter(email=email, code=codigo)
        if codigo_obj.exists():
            codigo_obj = codigo_obj.first()
            if not codigo_obj.codigo_expirou():
                codigo_obj.delete()
                messages.success(request, 'Código validado com sucesso. Agora redefina sua senha.')
                return redirect('redefinir_senha')
            else:
                messages.error(request, 'Código expirado. Tente novamente.')
        else:
            messages.error(request, 'Código inválido. Tente novamente.')

    return render(request, 'teacher/validar-codigo.html')


def redefinir_senha_view(request):
    # validar a senha antes de redefinir
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
                return redirect('submit_login')
            else:
                messages.error(request, 'As senhas não coindizem')
        else:
            messages.error(request, 'Algum campo está vazio')

    return render(request, 'teacher/redefinir-senha.html')


def enviar_email_form_contato(request):
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
            print("Erro ao enviar email:", e)
            messages.error(request, f"Ocorreu um erro ao enviar o email: {e}")

        return redirect("index")

    return redirect("index")
