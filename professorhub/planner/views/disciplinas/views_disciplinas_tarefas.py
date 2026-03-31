from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from planner.forms import TarefaForm
from planner.models import Disciplina, Tarefa
from planner.utils import criar_aviso_se_faltar_aulas

# ############################################################################################################################
#                                                  Disciplinas:tarefas
# ############################################################################################################################
@login_required(login_url='/login/')
def disciplina_tarefas_view(request, id):
    if request.method == 'POST':
        form = TarefaForm(request.POST)

        if form.is_valid():
            form.save()
        else: print(form.errors)

    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)

    # tarefas listadas
    print(Tarefa.objects.all())
    tarefas = Tarefa.objects.filter(disciplina=disciplina, disciplina__user=request.user)
    paginator = Paginator(tarefas, 10)
    page_number_tarefas = request.GET.get('page-tarefas', 1) 
    tarefas_page = paginator.get_page(page_number_tarefas)
    print('tarefas:',tarefas)

    # aviso
    criar_aviso_se_faltar_aulas(disciplina)
    return render(request, 'planner/disciplinas/disciplina_tarefas.html', {
        'disciplina': disciplina,
        'tarefas': tarefas_page,
    })


@login_required(login_url='/login/')
def disciplina_tarefas_detail_view(request, id, atv_id):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
        tarefa = get_object_or_404(Tarefa, id=atv_id, disciplina=disciplina)
        form = TarefaForm(request.POST, instance=tarefa)

        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.status = request.POST.get('status')
            tarefa.save()
        else: print(form.errors)
        
        return redirect('disciplina_tarefas', id=id)


@login_required(login_url='/login/')
def disciplina_tarefas_delete_view(request, id, atv_id):
    if request.method == 'POST':
        plano = get_object_or_404(Tarefa, id=atv_id, disciplina__user=request.user)
        plano.delete()
        return redirect('disciplina_tarefas', id=id)
