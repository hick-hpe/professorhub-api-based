from planner.models import Avaliacao, Disciplina, PlanoAula
from planner.forms import AvaliacaoForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# ############################################################################################################################
#                                                  Avaliações
# ############################################################################################################################

@login_required(login_url='/login/')
def avaliacoes_view(request):
    form = AvaliacaoForm()
    ('--- request ---')
    (request.POST)

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            (form.errors)

    avaliacoes = Avaliacao.objects.filter(disciplina__user=request.user).order_by('data')
    disciplinas = Disciplina.objects.filter(user=request.user)

    return render(request, 'planner/avaliacoes/avaliacoes.html', {
        'avaliacoes': avaliacoes,
        'disciplinas': disciplinas,
        'form': form,
    })

# CRUD Avaliação: GET/PUT
@login_required(login_url='/login/')
def avaliacao_detail_view(request, id):
    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        disciplina = get_object_or_404(Disciplina, id=disciplina_id, user=request.user)
        avaliacao = get_object_or_404(Avaliacao, id=id, disciplina=disciplina)
        form = AvaliacaoForm(request.POST, instance=avaliacao)

        if form.is_valid():
            avaliacao = form.save(commit=False)
            plano_aula = request.POST.get('plano_aula')
            etapa = request.POST.get('etapa')
            status = request.POST.get('status')
            avaliacao.plano_aula = get_object_or_404(PlanoAula, id=plano_aula)
            avaliacao.etapa = etapa
            avaliacao.status = status
            avaliacao.save()

    return redirect('avaliacoes')

# CRUD Avaliação: DELETE
@login_required(login_url='/login/')
def avaliacao_delete_view(request, id):
    if request.method == 'POST':
        avaliacao = get_object_or_404(Avaliacao, id=id, disciplina__user=request.user)
        avaliacao.delete()
        return redirect('avaliacoes')
