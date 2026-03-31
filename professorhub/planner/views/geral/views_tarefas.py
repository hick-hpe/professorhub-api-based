from planner.models import Tarefa, Disciplina, PlanoAula
from planner.forms import TarefaForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timezone

# ############################################################################################################################
#                                                  Tarefas
# ############################################################################################################################

# CRUD Tarefas: GET/POST
@login_required(login_url='/login/')
def tarefas_view(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        ('--- criar tarefa ---')
        (request.POST)

        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.user = request.user
            status = request.POST.get('status', 'criada')
            tarefa.status = status
            tarefa.save()
        else:
            (form.errors)

    tarefas = Tarefa.objects.filter(disciplina__user=request.user).order_by('prazo')
    for t in tarefas: t.atualizar_para_pendente_se_expirou()
    disciplinas = Disciplina.objects.filter(user=request.user)
    planos = PlanoAula.objects.filter(disciplina__user=request.user)

    form = TarefaForm()
    return render(request, 'planner/tarefas/tarefas.html', {
        'disciplinas': disciplinas,
        'tarefas': tarefas,
        'planos': planos,
        'form': form,
    })


@login_required(login_url='/login/')
def tarefas_mes_atual_view(request, mes):
    ('------------ tarefas_list ---------------')

    agora = timezone.now()
    tarefas = Tarefa.objects.filter(
        disciplina__user=request.user,
        prazo__year=agora.year,
        prazo__month=(mes+1)
    ).order_by('prazo')


    tarefas_list = []
    for t in tarefas:
        prazo_str = f'{t.prazo.year}-{t.prazo.month:02}-{t.prazo.day:02}'
        # (t.prazo.strftime('%a'))
        t.atualizar_para_pendente_se_expirou()

        tarefas_list.append({
            'nome': t.nome,
            'status': t.status,
            'prazo': prazo_str,
            'get_status_display': t.get_status_display(),
            'disciplina': t.disciplina.nome,
            'descricao': t.descricao,
            'diaSemana': t.prazo.strftime("%a")
        })

    for t in tarefas_list:
        (t['nome'])
        (t['prazo'])
        (t['status'])
        ("-----------------------------")
    
    return JsonResponse({
        'tarefas': tarefas_list
    })


@login_required(login_url='/login/')
def tarefas_mes_atual_view(request, mes):
    agora = datetime.now()
    tarefas = Tarefa.objects.filter(
        disciplina__user=request.user,
        prazo__year=agora.year,
        prazo__month=(mes+1)
    ).order_by('prazo')

    tarefas_list = []
    for t in tarefas:
        prazo_str = f'{t.prazo.year}-{t.prazo.month:02}-{t.prazo.day:02}'
        t.atualizar_para_pendente_se_expirou()

        tarefas_list.append({
            'nome': t.nome,
            'status': t.status,
            'prazo': prazo_str,
            'get_status_display': t.get_status_display(),
            'disciplina': t.disciplina.nome,
            'descricao': t.descricao,
            'diaSemana': t.prazo.strftime("%a")
        })
    
    return JsonResponse({
        'tarefas': tarefas_list
    })


# CRUD Tarefas: GET/PUT
@login_required(login_url='/login/')
def tarefa_detail_view(request, id):
    if request.method == 'POST':
        tarefa = get_object_or_404(Tarefa, id=id, disciplina__user=request.user)
        plano_aula_id = request.POST.get('plano_aula')
        status = request.POST.get('status')
        plano_aula = get_object_or_404(PlanoAula, id=plano_aula_id)
        form = TarefaForm(request.POST, instance=tarefa)
        ('--- atualiza tarefa ---')
        (request.POST)
        
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.user = request.user
            tarefa.plano_aula = plano_aula
            tarefa.status = status
            tarefa.save()
            ('status:', tarefa.status)
        
        (form.errors)

    return redirect('tarefas')

# CRUD Tarefas: DELETE
@login_required(login_url='/login/')
def tarefa_delete_view(request, id):
    if request.method == 'POST':
        tarefa = get_object_or_404(Tarefa, id=id, disciplina__user=request.user)
        tarefa.delete()
        return redirect('tarefas')
