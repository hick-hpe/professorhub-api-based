from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User

# ############################################################################################################################
#                                                  Configurações
# ############################################################################################################################

# CRUD Configurações: GET/POST
@login_required(login_url='/login/')
def configuracoes_view(request):
    errors_data = {
        'erro_user': False,
        'erro_email': False
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Verifica se outro usuário já usa esse username
        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            errors_data['erro_user'] = True

        # Verifica se outro usuário já usa esse email
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            errors_data['erro_email'] = True

        # Se não houver erro, atualiza os dados
        if not errors_data['erro_user'] and not errors_data['erro_email']:
            request.user.username = username
            request.user.email = email
            request.user.save()

    return render(request, 'planner/configuracoes.html', errors_data)


# CRUD Configurações: DELETE
@login_required(login_url='/login/')
def configuracoes_delete_view(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('submit_login')
