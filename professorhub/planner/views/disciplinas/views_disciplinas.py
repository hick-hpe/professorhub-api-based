from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from planner.models import Disciplina, CalendarioLetivo, DataImportante, PlanoAula
from planner.forms import DisciplinaForm
from datetime import timedelta
from planner.utils import (
    criar_aviso_se_faltar_aulas,
    get_dia_semana,
    get_dias_aula_na_semana_disciplina
)


# função para ajustar as datas das aulas de uma disciplina conforme os dias de aula selecionados
def ajustar_datas_das_aulas(disciplina, datas_aulas, dias_aulas):
    """
    Ajusta as datas das aulas conforme os dias selecionados
    Ex: aulas na segunda e quarta, mas com a mudança, caiu numa terça. Neste caso,
    as datas das aulas serão ajustadas, ao invés de serem excluídas a fim de manter
    a ordem das aulas e evitar a perda de dados. (como ementa, conteudos, etc)
    """
    index_proxima_data_adicionada = 0
    planos = list(disciplina.planos.all().order_by('data'))

    for (plano, data) in zip(planos, datas_aulas):
        plano.data = data[0]
        dia = get_dia_semana(plano.data)
        plano.num_aulas = dias_aulas[dia]
        index_proxima_data_adicionada += 1
    
    PlanoAula.objects.bulk_update(planos, ['data', 'num_aulas'])

    return index_proxima_data_adicionada


def calcular_datas_aulas(calendario, carga_horaria, dias_aulas, data_inicial, data_final):
    """
    Verifica se é possível cumprir a carga horária no período e dias informados
    """
    try:
        num_aulas = 0
        proximo_dia = data_inicial
        dias = dias_aulas.keys()
        datas_aulas = []

        # Validações básicas
        if not calendario:
            raise ValueError('Calendário letivo não fornecido.')
        
        if not dias_aulas or len(dias_aulas) == 0:
            raise ValueError('Nenhum dia de aula especificado.')
        
        if data_inicial > data_final:
            raise ValueError('Data inicial não pode ser maior que data final.')

        try:
            # obter os objetos 'DataImportante' que são dias não letivos
            dias_nao_letivos = set(
                DataImportante.objects.filter(calendario=calendario, dia_letivo=False)
                .values_list("data", flat=True)
            )
            
            # ===============================================
            # TODO: arrumar isso depois para períodos
            # ===============================================
            # obter os períodos não letivos
            periodos_nao_letivos = calendario.periodos.filter(calendario=calendario, eh_letivo=False)
            
            # obter os dias nesses intervalos
            dias_temp = set()
            for periodo in periodos_nao_letivos:
                di = periodo.data_inicio
                df = periodo.data_fim
                while di <= df:
                    dias_temp.add(di)
                    di += timedelta(days=1)

            # e juntar tudo
            dias_nao_letivos = dias_nao_letivos.union(dias_temp)
                                                              
        except Exception as e:
            print(f'Erro ao buscar dias não letivos: {str(e)}')
            dias_nao_letivos = set()  # Continua sem os dias não letivos se houver erro

        print('------ Data das aulas calcular_datas_aulas ------')
        while num_aulas < carga_horaria and proximo_dia <= data_final:
            dia_semana = get_dia_semana(proximo_dia)

            if dia_semana in dias and proximo_dia not in dias_nao_letivos:
                try:
                    aulas_no_dia = int(dias_aulas[dia_semana])
                    if aulas_no_dia <= 0:
                        raise ValueError(f'Número de aulas inválido para {dia_semana}: {aulas_no_dia}')
                    
                    print(f'Aula: {proximo_dia:%d/%m/%Y} -> [{dia_semana}] - {aulas_no_dia} aula(s)')
                    num_aulas += aulas_no_dia
                    datas_aulas.append((proximo_dia, aulas_no_dia))
                except (ValueError, KeyError) as e:
                    print(f'Erro ao processar dia {dia_semana}: {str(e)}')
                    # Pula este dia e continua

            proximo_dia += timedelta(days=1)

        return datas_aulas
        
    except Exception as e:
        print(f'Erro em calcular_datas_aulas: {str(e)}')
        raise Exception(f'Erro ao calcular datas das aulas: {str(e)}')


# função para validar os dados da disciplina (nome, calendário, dias da semana, número de aulas por dia, datas do calendário)
# tentar generarlizar essa função para ser usada tanto na criação quanto na edição de disciplina (rever)
def validar_dados_criar_disciplina(disciplina, data, request):
    # nome da disciplinas nao pode ser muito extenso
    if len(disciplina.nome) > 50:
        return { 'error': 'O nome da disciplina não pode exceder 50 caracteres.' }
    
    # evitar disciplinas com mesmo nome
    minhas_disciplinas = Disciplina.objects.filter(user=request.user)
    nomes_disciplinas_banco = set([d.nome.lower() for d in minhas_disciplinas])
    if disciplina.nome.lower() in nomes_disciplinas_banco:
        return { 'error': 'Não é possível cadastrar disciplinas com mesmo nome!' }
    
    # verificar se calendário foi selecionado
    calendario_pk = data.get('calendario')
    if not calendario_pk:
        return {'error': 'Por favor, selecione um calendário letivo.'}

    # obter calendário selecionado e validar se pertence ao usuário
    calendario = CalendarioLetivo.objects.filter(pk=calendario_pk, user=request.user).first()
    if not calendario:
        return {'error': 'Calendário letivo não encontrado ou sem permissão.'}

    # validar dias da semana selecionados 
    dias = set(request.POST.getlist('dias[]'))
    if not dias:
        return {'error': 'Selecione ao menos um dia da semana para as aulas.'}

    # validar o número de aulas por dia
    dias_aulas = {}
    for dia in dias:
        num_aulas = data.get(f'aulas_{dia}')
        try:
            num = int(num_aulas)
            if not (1 <= num <= 6):
                raise ValueError()
        except Exception:
            return {'error': f'Por favor, informe um número válido de aulas [1-6] para {dia}.'}
        dias_aulas[dia] = num

    # validar datas do calendário
    if (not calendario.data_inicio or not calendario.data_fim) or (calendario.data_inicio >= calendario.data_fim):
        return {'error': 'O calendário letivo selecionado possui datas inválidas.'}

    # se chegou aqui, é porque os dados são válidos
    disciplina.calendario = calendario
    disciplina.save()
    
    return {
        'disciplina': disciplina,
        'dias_aulas': dias_aulas
    }



# ############################################################################################################################
#                                                  Disciplinas
# ############################################################################################################################


# CRUD Disciplinas: GET/POST
@login_required(login_url='/login/')
@transaction.atomic
def disciplinas_view(request):
    # se a requisicao for GET, renderizar a página com as disciplinas do usuário
    if request.method == 'GET':
        disciplinas = Disciplina.objects.filter(user=request.user)
        calendarios = CalendarioLetivo.objects.filter(user=request.user)
        form = DisciplinaForm()

        # listar dias nos quais tem aula
        dias_disciplinas = []
        for disciplina in disciplinas:
            dias = get_dias_aula_na_semana_disciplina(disciplina)
            dias_list = list(dias)
            dias_str = ', '.join(dias_list)

            dias_disciplinas.append(
                (disciplina, dias_str)
            )
            
            # aviso (rever)
            criar_aviso_se_faltar_aulas(disciplina)

        return render(request, 'planner/disciplinas/disciplinas.html', {
            'disciplinas': disciplinas,
            'calendarios': calendarios,
            'form': form,
            'dias_disciplinas': dias_disciplinas
        })


    # se a requisicao for POST, criar nova disciplina (após validar os dados) e gerar aulas
    elif request.method == 'POST':
        data_request = request.POST
        form = DisciplinaForm(data_request)

        if not form.is_valid():
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            return redirect('disciplinas')
        
        # form válido
        disciplina = form.save(commit=False)
        disciplina.user = request.user

        # validar dados da disciplina (nome, calendário, dias da semana, número de aulas por dia, datas do calendário)
        # tentar generarlizar essa função para ser usada tanto na criação quanto na edição de disciplina (rever)
        dados_or_error = validar_dados_criar_disciplina(disciplina, data_request, request)
        
        # se os dados forem inválidos, mostrar mensagem de erro e retornar para a página sem criar disciplina
        if (dados_or_error.get('error')):
            messages.error(request, dados_or_error['error'])
            return redirect('disciplinas')
        
        # se os dados forem válidos, obter disciplina e gerar aulas
        disciplina = dados_or_error['disciplina']
        dias_aulas = dados_or_error['dias_aulas']

        # tentar gerar aulas (em caso de erro, excluir disciplina criada e informar)
        try:
            num_aulas, carga_horaria = eh_possivel_carga_horaria(
                disciplina.calendario,
                disciplina.carga_horaria,
                dias_aulas,
                disciplina.calendario.data_inicio,
                disciplina.calendario.data_fim
            )

            if num_aulas >= carga_horaria:
                messages.success(request, 'Disciplina criada com sucesso! Todas as aulas foram programadas.')
            else:
                aulas_faltantes = abs(num_aulas - carga_horaria)
                disciplina.aviso = f"Faltam {aulas_faltantes} aula(s) para cumprir a carga horária."
                disciplina.save()
                messages.warning(request, f'Disciplina criada, mas faltam {aulas_faltantes} aula(s) para cumprir a carga horária completa.')

            gerar_aulas(disciplina, disciplina.carga_horaria, dias_aulas)

        except Exception as e:
            # se algo deu errado ao gerar aulas, remover disciplina criada e avisar o usuário
            if disciplina.pk:
                disciplina.delete()
            messages.error(request, f'Erro ao gerar as aulas: {str(e)}')
            return redirect('disciplinas')
    
    return redirect('disciplinas')


# CRUD Disciplinas: DELETE
@login_required(login_url='/login/')
def disciplina_delete_view(request, id):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
        disciplina.delete()
        return redirect('disciplinas')


# AJAX: GET disciplinas do usuário
def disciplinas_api_view(request):
    disciplinas = Disciplina.objects.filter(user=request.user)
    return JsonResponse({
        'disciplinas': list(disciplinas.values('id', 'nome'))
    })
