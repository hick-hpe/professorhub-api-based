from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from planner.models import Disciplina, Avaliacao, PlanoAula
from planner.forms import AvaliacaoForm
from planner.utils import criar_aviso_se_faltar_aulas

# ############################################################################################################################
#                                                  Disciplinas:avaliações
# ############################################################################################################################
@login_required(login_url='/login/')
def disciplina_avaliacoes_view(request, id):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)

        if form.is_valid():
            form.save()
        
        else: print(form.errors)

    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)

    avaliacoes = Avaliacao.objects.filter(disciplina=disciplina, disciplina__user=request.user).order_by('data')
    planos = PlanoAula.objects.filter(disciplina=disciplina, disciplina__user=request.user)
    paginator = Paginator(avaliacoes, 10)
    page_number_avaliacoes = request.GET.get('page-avaliacoes', 1) 
    avaliacoes_page = paginator.get_page(page_number_avaliacoes)

    # aviso
    criar_aviso_se_faltar_aulas(disciplina)

    return render(request, 'planner/disciplinas/disciplina_avaliacoes.html', {
        'disciplina': disciplina,
        'avaliacoes': avaliacoes_page,
        'planos': planos,
    })


@login_required(login_url='/login/')
def disciplina_avaliacao_detail_view(request, id, av_id):
    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        disciplina = get_object_or_404(Disciplina, id=disciplina_id, user=request.user)
        avaliacao = get_object_or_404(Avaliacao, id=av_id, disciplina=disciplina)
        form = AvaliacaoForm(request.POST, instance=avaliacao)

        if form.is_valid():
            avaliacao = form.save(commit=False)
            plano_aula = request.POST.get('plano_aula')
            etapa = request.POST.get('etapa')
            avaliacao.plano_aula = get_object_or_404(PlanoAula, id=plano_aula)
            avaliacao.etapa = etapa
            avaliacao.save()

    return redirect('disciplina_avaliacoes', id=id)


@login_required(login_url='/login/')
def disciplina_avaliacao_delete_view(request, id, av_id):
    if request.method == 'POST':
        avaliacao = get_object_or_404(Avaliacao, id=av_id, disciplina__id=id, disciplina__user=request.user)
        avaliacao.delete()
        return redirect('disciplina_avaliacoes', id=id)

