from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from planner.models import Disciplina
from planner.forms import DisciplinaForm
from planner.utils import (
    get_dias_aula_na_semana_disciplina,
    eh_possivel_carga_horaria,
    gerar_aulas,
    num_aulas_por_dia_disciplina,
    criar_aviso_se_faltar_aulas,
)

# ############################################################################################################################
#                                                  Disciplinas:configurações
# ############################################################################################################################

@login_required(login_url='/login/')
def disciplina_configuracoes_view(request, id):

    print('>_ disciplina_configuracoes')

    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
     
    if request.method == 'POST':
        print('>_ configuracoes')
        print(request.POST)

        dias_aulas_antigo = get_dias_aula_na_semana_disciplina(disciplina)
        dias_aulas_req = set(request.POST.getlist('dias[]'))
        ch_antiga = disciplina.carga_horaria
        dias_aulas = {}

        data = request.POST
        form = DisciplinaForm(data, instance=disciplina)

        if form.is_valid():
            print('form válido')
            disciplina = form.save(commit=False)
            disciplina.user = request.user
            ch_atual = disciplina.carga_horaria
            carga_diff = ch_atual - ch_antiga
            data_inicial = timezone.localdate()

            # mudar a partir de hoje, se e somente se "data_inicial" estiver no intervalo das datas
            if data_inicial < disciplina.calendario.data_inicio:
                data_inicial = disciplina.calendario.data_inicio

            ch_atualizada = carga_diff
            disciplina.save()

            # print valores iniciais e vaores recebidos agr
            print('--- valores ---')
            print('carga horária antiga:', ch_antiga)
            print('carga horária atual:', ch_atual)
            print('dias aulas antigos:', dias_aulas_antigo)
            print('dias aulas req:', dias_aulas_req)
            print('---------------')
            
            # se carga horária diminuiu? excluir as excedentes
            if carga_diff < 0:
                print('--- diminuir carga horária ---')
                # exclui as excedentes
                carga_diff = -carga_diff
                while carga_diff > 0:
                    # 'data' ou 'id'??
                    # últimas adicionadas ou últimas datas??
                    plano = disciplina.planos.all().order_by('-data').first()
                    if plano:
                        plano.delete()
                    carga_diff -= 1

            # se carga horária aumentou? verificar se é possível criar todas
            else:
                print('--- aumentar carga horária ---')
                # atualizar os dias da semana de aula
                dias = dias_aulas_antigo
                if dias_aulas_antigo != dias_aulas_req:
                    dias = dias_aulas_req
                
                # contar quantidade de aulas por dia
                for dia in dias:
                    num_aulas = data.get(f'aulas_{dia}')
                    dias_aulas[dia] = int(num_aulas)
                print('dias aulas finais:', dias_aulas)

                (num_aulas, carga_horaria) = eh_possivel_carga_horaria(
                    disciplina.calendario,
                    ch_atual,
                    dias_aulas,
                    data_inicial,
                    disciplina.calendario.data_fim
                )
                print(f'num aulas possíveis: {num_aulas}, carga horária: {carga_horaria}')
                if num_aulas < carga_horaria:
                    messages.error(request, 'Não é possível atualizar para cumprir essa carga horária!')
                    return redirect('disciplina_configuracoes', id=id)
                else:
                    ch_atualizada = ch_atual
                
            print('>_ config - gerar_aulas')
            gerar_aulas(disciplina, ch_atualizada, dias_aulas, data_inicial=data_inicial)

        else:
            print('>_ config - form inválido')
            print(form.errors)

    
    # listar dias nos quais tem aula
    dias_aulas = num_aulas_por_dia_disciplina(disciplina, tirar_dias_zerados=False)

    # aviso
    criar_aviso_se_faltar_aulas(disciplina)

    return render(request, 'planner/disciplinas/disciplina_configuracoes.html', {
        'disciplina': disciplina,
        'dias': dias_aulas.items()
    })
