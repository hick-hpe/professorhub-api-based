
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from planner.models import Disciplina, Ementa
from planner.forms import EmentaForm


# ############################################################################################################################
#                                                  Disciplinas:ementas
# ############################################################################################################################

# listagem e criação de ementas
@login_required(login_url='/login/')
def disciplina_ementas_view(request, id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    
    if request.method == 'POST':
        form = EmentaForm(request.POST)
        if form.is_valid():
            ementa = form.save(commit=False)
            ementa.disciplina = disciplina
            ementa.save()
            messages.success(request, 'Ementa adicionada com sucesso!')
            return redirect('disciplina_ementas', id=id)
        else:
            messages.error(request, 'Erro ao adicionar ementa.')
    
    ementas = disciplina.ementas.all()
    total_ementas = ementas.count()
    ementas_abordadas = ementas.filter(abordado=True).count()
    percentual = (ementas_abordadas / total_ementas * 100) if total_ementas > 0 else 0
    
    form = EmentaForm()
    return render(request, 'planner/disciplinas/disciplina_ementas.html', {
        'disciplina': disciplina,
        'ementas': ementas,
        'form': form,
        'total_ementas': total_ementas,
        'ementas_abordadas': ementas_abordadas,
        'percentual': percentual,
    })


# marcar como abordado/não abordado
@login_required(login_url='/login/')
def ementa_marcar_abordado_view(request, id, ementa_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    ementa = get_object_or_404(Ementa, id=ementa_id, disciplina=disciplina)
    
    if request.method == 'POST':
        ementa.abordado = not ementa.abordado
        ementa.save()
    
    return redirect('disciplina_ementas', id=id)


# editar ementa
@login_required(login_url='/login/')
def ementa_editar_view(request, id, ementa_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    ementa = get_object_or_404(Ementa, id=ementa_id, disciplina=disciplina)
    
    if request.method == 'POST':
        form = EmentaForm(request.POST, instance=ementa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ementa atualizada com sucesso!')
        else:
            messages.error(request, 'Erro ao atualizar ementa.')
    
    return redirect('disciplina_ementas', id=id)


# excluir ementa
@login_required(login_url='/login/')
def ementa_excluir_view(request, id, ementa_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    ementa = get_object_or_404(Ementa, id=ementa_id, disciplina=disciplina)
    
    if request.method == 'POST':
        ementa.delete()
        messages.success(request, 'Ementa excluída com sucesso!')
    
    return redirect('disciplina_ementas', id=id)
