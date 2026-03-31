from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from planner.models import DataImportante, Disciplina, PlanoAula
from django.core.paginator import Paginator
from planner.forms import PlanoAulaForm
from planner.utils import (
    get_dias_aula_na_semana_disciplina,
    criar_aviso_se_faltar_aulas,
    alterar_datas_apos_exclusao_plano_aula,
    get_dia_semana
)
from datetime import timedelta
from django.http import JsonResponse


# AJAX: GET planos de aula de uma disciplina
@login_required(login_url='/login/')
def disciplina_planos_json(request, id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    planos = disciplina.planos.all().order_by('data')

    return JsonResponse({
        'planos': list(planos.values('id', 'titulo'))
    })


# views disciplina planos
@login_required(login_url='/login/')
def disciplina_planos_view(request, id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)

    if request.method == 'POST':
        form = PlanoAulaForm(request.POST)

        if form.is_valid():
            plano = form.save(commit=False)
            plano.disciplina = disciplina
            plano.status = 'criado'
            plano.objetivos = request.POST.get('objetivos')
            plano.conteudos = request.POST.get('conteudos')
            plano.num_aulas = request.POST.get('num_aulas')
            plano.save()

    # aulas listadas
    aulas = disciplina.planos.all().order_by('data')
    paginator = Paginator(aulas, 10)
    page_number = request.GET.get('page-aulas', 1) 
    aulas_page = paginator.get_page(page_number)
    dias_selecionados = get_dias_aula_na_semana_disciplina(disciplina)
    aulas_dias_selecionados = disciplina.planos.values_list('num_aulas', flat=True)

    dias = {
        'segunda': 0,
        'terca': 0,
        'quarta': 0,
        'quinta': 0,
        'sexta': 0,
    }

    for dia, num_aulas in zip(dias_selecionados, aulas_dias_selecionados):
        dias[dia] = num_aulas

    # aviso
    criar_aviso_se_faltar_aulas(disciplina)

    return render(request, 'planner/disciplinas/disciplina_planos.html', {
        'disciplina': disciplina,
        'aulas': aulas_page
    })



# views disciplina planos - editar, excluir, swap, duplicar
@login_required(login_url='/login/')
def disciplina_planos_detail_view(request, id, plano_id):
    if request.method == 'POST':
        plano = get_object_or_404(PlanoAula, id=plano_id, disciplina__user=request.user)
        form = PlanoAulaForm(request.POST, instance=plano)

        if form.is_valid():
            plano = form.save(commit=False)
            plano.status = request.POST.get('status')
            plano.save()
        
        print(form.errors)
        
        return redirect('disciplina_planos', id=id)


# excluir plano aula e alterar datas dos planos seguintes
@login_required(login_url='/login/')
def disciplina_planos_excluir_view(request, id, plano_id):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, user=request.user, id=id)
        plano = get_object_or_404(PlanoAula, id=plano_id, disciplina=disciplina)
        data_excluida = plano.data
        plano.delete()

        # alterar a data dos planos de aulas a partir da data excluída
        alterar_datas_apos_exclusao_plano_aula(disciplina, data_excluida)

        return redirect('disciplina_planos', id=id)


# trocar a data de um plano aula com o plano anterior ou posterior
@login_required(login_url='/login/')
def disciplina_planos_swap_view(request, id, plano_id, direction):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, user=request.user, id=id)
        plano1 = get_object_or_404(PlanoAula, id=plano_id, disciplina=disciplina)
        
        # Obter todos os planos ordenados por data
        planos = list(disciplina.planos.all().order_by('data'))
        
        # Encontrar o índice do plano atual
        try:
            index = planos.index(plano1)
        except ValueError:
            return redirect('disciplina_planos', id=id)
        
        # Determinar qual plano trocar baseado na direção
        if direction == 'up' and index > 0:
            plano2 = planos[index - 1]
        elif direction == 'down' and index < len(planos) - 1:
            plano2 = planos[index + 1]
        else:
            return redirect('disciplina_planos', id=id)
        
        # Trocar as datas entre os dois planos
        plano1.data, plano2.data = plano2.data, plano1.data
        
        plano1.save()
        plano2.save()
        
        return redirect('disciplina_planos', id=id)


# duplicar plano aula e alterar a data do plano duplicado para o próximo dia letivo da disciplina, e ajustar as datas dos planos seguintes
@login_required(login_url='/login/')
def disciplina_planos_duplicar_view(request, id, plano_id):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, user=request.user, id=id)
        plano_original = get_object_or_404(PlanoAula, id=plano_id, disciplina=disciplina)

        planos_ordenados = list(disciplina.planos.all().order_by('data'))
        
        try:
            index = planos_ordenados.index(plano_original)
        except ValueError:
            return redirect('disciplina_planos', id=id)

        dias_aulas_disciplina = get_dias_aula_na_semana_disciplina(disciplina)
        
        dias_nao_letivos = set(
            DataImportante.objects.filter(calendario=disciplina.calendario, dia_letivo=False)
            .values_list("data", flat=True)
        )
        
        proximo_dia = plano_original.data + timedelta(days=1)
        nova_data = None
        
        while nova_data is None:
            dia_semana = get_dia_semana(proximo_dia)
            
            if dia_semana in dias_aulas_disciplina and proximo_dia not in dias_nao_letivos:
                nova_data = proximo_dia
            else:
                proximo_dia += timedelta(days=1)

        plano_duplicado = PlanoAula.objects.create(
            disciplina=disciplina,
            data=nova_data,
            titulo=f"{plano_original.titulo} (cópia)",
            objetivos=plano_original.objetivos,
            conteudos=plano_original.conteudos,
            status=plano_original.status,
            num_aulas=plano_original.num_aulas
        )

        planos_seguintes = planos_ordenados[index + 1:]
        
        if planos_seguintes:
            for plano in planos_seguintes:
                proximo_dia = nova_data + timedelta(days=1)
                nova_data_seguinte = None
                
                while nova_data_seguinte is None:
                    dia_semana = get_dia_semana(proximo_dia)
                    
                    if dia_semana in dias_aulas_disciplina and proximo_dia not in dias_nao_letivos:
                        nova_data_seguinte = proximo_dia
                    else:
                        proximo_dia += timedelta(days=1)
                
                plano.data = nova_data_seguinte
                plano.save()
                nova_data = nova_data_seguinte
        
        return redirect('disciplina_planos', id=id)
