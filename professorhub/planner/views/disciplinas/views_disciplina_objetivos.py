from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from planner.forms import ObjetivoForm
from planner.models import Disciplina, Objetivo
from django.contrib import messages


# ############################################################################################################################
#                                                  Disciplinas:objetivos
# ############################################################################################################################

# CRUD Objetivos: GET/POST
@login_required(login_url='/login/')
def disciplina_objetivos_view(request, id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    
    if request.method == 'POST':
        form = ObjetivoForm(request.POST)
        if form.is_valid():
            objetivo = form.save(commit=False)
            objetivo.disciplina = disciplina
            objetivo.save()
            messages.success(request, 'Objetivo adicionado com sucesso!')
            return redirect('disciplina_objetivos', id=id)
        else:
            messages.error(request, 'Erro ao adicionar objetivo.')
    
    objetivos = disciplina.objetivos.all()
    total_objetivos = objetivos.count()
    objetivos_alcancados = objetivos.filter(alcancado=True).count()
    percentual = (objetivos_alcancados / total_objetivos * 100) if total_objetivos > 0 else 0
    
    form = ObjetivoForm()
    return render(request, 'planner/disciplinas/disciplina_objetivos.html', {
        'disciplina': disciplina,
        'objetivos': objetivos,
        'form': form,
        'total_objetivos': total_objetivos,
        'objetivos_alcancados': objetivos_alcancados,
        'percentual': percentual,
    })


# CRUD Objetivos: PUT
@login_required(login_url='/login/')
def objetivo_marcar_alcancado_view(request, id, objetivo_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    objetivo = get_object_or_404(Objetivo, id=objetivo_id, disciplina=disciplina)
    
    if request.method == 'POST':
        objetivo.alcancado = not objetivo.alcancado
        objetivo.save()
    
    return redirect('disciplina_objetivos', id=id)


# CRUD Objetivos: PUT
@login_required(login_url='/login/')
def objetivo_editar_view(request, id, objetivo_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    objetivo = get_object_or_404(Objetivo, id=objetivo_id, disciplina=disciplina)
    
    if request.method == 'POST':
        form = ObjetivoForm(request.POST, instance=objetivo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Objetivo atualizado com sucesso!')
        else:
            messages.error(request, 'Erro ao atualizar objetivo.')
    
    return redirect('disciplina_objetivos', id=id)


# CRUD Objetivos: DELETE
@login_required(login_url='/login/')
def objetivo_excluir_view(request, id, objetivo_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    objetivo = get_object_or_404(Objetivo, id=objetivo_id, disciplina=disciplina)
    
    if request.method == 'POST':
        objetivo.delete()
        messages.success(request, 'Objetivo excluído com sucesso!')
    
    return redirect('disciplina_objetivos', id=id)

