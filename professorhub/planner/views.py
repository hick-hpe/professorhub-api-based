from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from .forms import *
from datetime import datetime, timedelta
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import logout
from django.core.paginator import Paginator
import calendar
from django.db.models import Count, Sum
from datetime import timedelta

# View Dashboard Admin
@login_required(login_url='/login/')
def admin_dashboard_view(request):
    return render(request, 'planner/admin_dashboard.html')

# AJAX: GET todos os planos de aulas
@login_required(login_url='/login/')
def planos_json(request):
    planos = PlanoAula.objects.filter(disciplina__user=request.user).order_by('data')
    return JsonResponse({
        'planos': list(planos.values('id', 'titulo', 'data', 'disciplina__nome', 'status'))
    })

# AJAX: GET datas importantes do mês
@login_required(login_url='/login/')
def datas_importantes_mes_view(request, mes):
    agora = timezone.now()
    datas = DataImportante.objects.filter(
        calendario__user=request.user,
        data__year=agora.year,
        data__month=(mes+1)
    ).order_by('data')

    datas_list = []
    for d in datas:
        data_str = f'{d.data.year}-{d.data.month:02}-{d.data.day:02}'
        datas_list.append({
            'data': data_str,
            'detalhes': d.detalhes,
            'dia_letivo': d.dia_letivo,
        })

    return JsonResponse({
        'datas': datas_list
    })

# ############################################################################################################################
#                                                  Disciplinas
# ############################################################################################################################

# Número de aulas faltantes
def calcular_num_aulas_faltantes(disciplina):
    total = disciplina.carga_horaria

    aulas_criadas = PlanoAula.objects.filter(
        disciplina=disciplina,
    ).aggregate(num_aulas=Sum('num_aulas'))['num_aulas'] or 0
    
    print('total:', total)
    print('aulas_criadas:', aulas_criadas)
    aulas_faltantes = total - aulas_criadas
    
    nome = f'[{disciplina.nome}]'
    carga = f'total={total:02}'
    print(f'[{str(disciplina.pk).rjust(2)}] | {nome.ljust(15)} | {carga:02}h | {aulas_criadas:02} | -> faltam {aulas_faltantes} aula(s)')
    return aulas_faltantes


# criar aviso
def criar_aviso_se_faltar_aulas(disciplina):
    aulas_faltantes = calcular_num_aulas_faltantes(disciplina)
    mensagem = ''
    if aulas_faltantes > 0:
        mensagem = f"Faltam {aulas_faltantes} aula{'s' if aulas_faltantes != 1 else ''} para cumprir a carga horária!"

    if aulas_faltantes > 0:
        if not disciplina.aviso:
            disciplina.aviso = mensagem
            disciplina.save()
    else:
        print('tudo ok aulas')
        disciplina.aviso = ''
        disciplina.save()

# CRUD Disciplinas: GET/POST
@login_required(login_url='/login/')
@transaction.atomic
def disciplinas_view(request):
    def _render_page():
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
            
            # aviso
            criar_aviso_se_faltar_aulas(disciplina)

        return render(request, 'planner/disciplinas/disciplinas.html', {
            'disciplinas': disciplinas,
            'calendarios': calendarios,
            'form': form,
            'dias_disciplinas': dias_disciplinas
        })


    if request.method == 'POST':
        data = request.POST
        form = DisciplinaForm(data)

        if not form.is_valid():
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            return _render_page()
        
        # form válido
        disciplina = form.save(commit=False)
        disciplina.user = request.user

        # evitar disciplinas com mesmo nome
        minhas_disciplinas = Disciplina.objects.filter(user=request.user)
        nomes_disciplinas_banco = set([d.nome.lower() for d in minhas_disciplinas])
        if disciplina.nome.lower() in nomes_disciplinas_banco:
            messages.error(request, 'Não é possível cadastrar disciplinas com mesmo nome!')
            return _render_page()

        # calendário
        calendario_pk = data.get('calendario')
        if not calendario_pk:
            messages.error(request, 'Por favor, selecione um calendário letivo.')
            return _render_page()

        calendario = CalendarioLetivo.objects.filter(pk=calendario_pk, user=request.user).first()
        if not calendario:
            messages.error(request, 'Calendário letivo não encontrado ou sem permissão.')
            return _render_page()

        # dias selecionados
        dias = set(request.POST.getlist('dias[]'))
        if not dias:
            messages.error(request, 'Selecione ao menos um dia da semana para as aulas.')
            return _render_page()

        # número de aulas por dia
        dias_aulas = {}
        for dia in dias:
            num_aulas = data.get(f'aulas_{dia}')
            try:
                num = int(num_aulas)
                if num <= 0 or num > 10:
                    raise ValueError()
            except Exception:
                messages.error(request, f'Por favor, informe um número válido de aulas para {dia}.')
                return _render_page()
            dias_aulas[dia] = num

        # validar datas do calendário
        if not calendario.data_inicio or not calendario.data_fim or calendario.data_inicio >= calendario.data_fim:
            messages.error(request, 'O calendário letivo selecionado possui datas inválidas.')
            return _render_page()

        # salvar disciplina
        disciplina.calendario = calendario
        disciplina.save()

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
            return _render_page()
    
    return _render_page()


# CRUD Disciplinas: DELETE
@login_required(login_url='/login/')
def disciplina_delete(request, id):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
        disciplina.delete()
        return redirect('disciplinas')


# ############################################################################################################################
#                                                  Planos de Aula (JSON)
# ############################################################################################################################
# AJAX: GET planos de aula de uma disciplina
@login_required(login_url='/login/')
def disciplina_planos_json(request, id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    planos = disciplina.planos.all().order_by('data')

    return JsonResponse({
        'planos': list(planos.values('id', 'titulo'))
    })


@login_required(login_url='/login/')
def disciplina_planos(request, id):
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

@login_required(login_url='/login/')
def disciplina_planos_detail(request, id, plano_id):
    if request.method == 'POST':
        plano = get_object_or_404(PlanoAula, id=plano_id, disciplina__user=request.user)
        form = PlanoAulaForm(request.POST, instance=plano)

        if form.is_valid():
            plano = form.save(commit=False)
            plano.status = request.POST.get('status')
            plano.save()
        
        print(form.errors)
        
        return redirect('disciplina_planos', id=id)


@login_required(login_url='/login/')
def disciplina_planos_excluir(request, id, plano_id):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, user=request.user, id=id)
        plano = get_object_or_404(PlanoAula, id=plano_id, disciplina=disciplina)
        data_excluida = plano.data
        plano.delete()

        # alterar a data dos planos de aulas a partir da data excluída
        alterar_datas_apos_exclusao_plano_aula(disciplina, data_excluida)

        return redirect('disciplina_planos', id=id)


def alterar_datas_apos_exclusao_plano_aula(disciplina, data_excluida):
    print(f'Alterações em {disciplina}')
    print(f'Data excluída: {data_excluida}')

    planos = list(disciplina.planos.filter(data__gt=data_excluida).order_by('data'))

    if not planos:
        return
    
    datas = [data_excluida] + list(disciplina.planos.filter(data__gt=data_excluida).order_by('data')
                 .values_list('data', flat=True))

    for plano, data in zip(planos, datas):
        print(f'Plano[data]={plano.data} recebe data={data}')
        plano.data = data

    PlanoAula.objects.bulk_update(planos, ['data'])


@login_required(login_url='/login/')
def disciplina_planos_swap(request, id, plano_id, direction):
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


@login_required(login_url='/login/')
def disciplina_planos_duplicar(request, id, plano_id):
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


# ############################################################################################################################
#                                                  Disciplinas:configurações
# ############################################################################################################################

@login_required(login_url='/login/')
def disciplina_configuracoes(request, id):

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
            # data_inicial > disciplina.calendario.data_fim:
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
                
            gerar_aulas(disciplina, ch_atualizada, dias_aulas, data_inicial=data_inicial)
        else:
            print(form.errors)

    dias = {
        'segunda': 0,
        'terca': 0,
        'quarta': 0,
        'quinta': 0,
        'sexta': 0,
        # 'sábado': 0 # sábados letivos
    }

    # apenas os 5 primeiros são suficientes para definir os dias de aulas
    # presumindo ter no máximo 5 aulas nos 5 dias da semana
    for plano in disciplina.planos.all()[:5]:
        dia = get_dia_semana(plano.data)
        dias[dia] = plano.num_aulas

    # aviso
    criar_aviso_se_faltar_aulas(disciplina)

    return render(request, 'planner/disciplinas/disciplina_configuracoes.html', {
        'disciplina': disciplina,
        'dias': dias.items()
    })

# ############################################################################################################################
#                                                  Disciplinas:conteúdos
# ############################################################################################################################

@login_required(login_url='/login/')
def disciplina_ementas(request, id):
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

@login_required(login_url='/login/')
def ementa_marcar_abordado(request, id, ementa_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    ementa = get_object_or_404(Ementa, id=ementa_id, disciplina=disciplina)
    
    if request.method == 'POST':
        ementa.abordado = not ementa.abordado
        ementa.save()
    
    return redirect('disciplina_ementas', id=id)

@login_required(login_url='/login/')
def ementa_editar(request, id, ementa_id):
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

@login_required(login_url='/login/')
def ementa_excluir(request, id, ementa_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    ementa = get_object_or_404(Ementa, id=ementa_id, disciplina=disciplina)
    
    if request.method == 'POST':
        ementa.delete()
        messages.success(request, 'Ementa excluída com sucesso!')
    
    return redirect('disciplina_ementas', id=id)

# ############################################################################################################################
#                                                  Disciplinas:objetivos
# ############################################################################################################################

@login_required(login_url='/login/')
def disciplina_objetivos(request, id):
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

@login_required(login_url='/login/')
def objetivo_marcar_alcancado(request, id, objetivo_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    objetivo = get_object_or_404(Objetivo, id=objetivo_id, disciplina=disciplina)
    
    if request.method == 'POST':
        objetivo.alcancado = not objetivo.alcancado
        objetivo.save()
    
    return redirect('disciplina_objetivos', id=id)

@login_required(login_url='/login/')
def objetivo_editar(request, id, objetivo_id):
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

@login_required(login_url='/login/')
def objetivo_excluir(request, id, objetivo_id):
    disciplina = get_object_or_404(Disciplina, id=id, user=request.user)
    objetivo = get_object_or_404(Objetivo, id=objetivo_id, disciplina=disciplina)
    
    if request.method == 'POST':
        objetivo.delete()
        messages.success(request, 'Objetivo excluído com sucesso!')
    
    return redirect('disciplina_objetivos', id=id)

# ############################################################################################################################
#                                                  Disciplinas:tarefas
# ############################################################################################################################
@login_required(login_url='/login/')
def disciplina_tarefas(request, id):
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
def disciplina_tarefas_detail(request, id, atv_id):
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
def disciplina_tarefas_delete(request, id, atv_id):
    if request.method == 'POST':
        plano = get_object_or_404(Tarefa, id=atv_id, disciplina__user=request.user)
        plano.delete()
        return redirect('disciplina_tarefas', id=id)

# ############################################################################################################################
#                                                  Disciplinas:avaliações
# ############################################################################################################################
@login_required(login_url='/login/')
def disciplina_avaliacoes(request, id):
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
def disciplina_avaliacao_detail(request, id, av_id):
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
def disciplina_avaliacao_delete(request, id, av_id):
    if request.method == 'POST':
        avaliacao = get_object_or_404(Avaliacao, id=av_id, disciplina__id=id, disciplina__user=request.user)
        avaliacao.delete()
        return redirect('disciplina_avaliacoes', id=id)


# ############################################################################################################################
#                                                  Calendário Letivo
# ############################################################################################################################

# CRUD Calendarios: GET/POST
@login_required(login_url='/login/')
def calendarios_view(request):
    if request.method == 'POST':
        form = CalendarioLetivoForm(request.POST)

        if form.is_valid():
            calendario = form.save(commit=False)
            calendario.user = request.user
            calendario.save()

            form = CalendarioLetivoForm()

    else:
        form = CalendarioLetivoForm()
    
    calendarios = CalendarioLetivo.objects.filter(user=request.user)
    calendarios_e_datas = []
    for calendario in calendarios:
        hoje = date.today()
        proxima = calendario.datas.filter(data__gte=hoje).order_by('data').first()
        calendarios_e_datas.append((calendario, proxima))
    
    print(calendarios_e_datas)
    
    form = CalendarioLetivoForm()
    return render(request, 'planner/calendarios/listar_calendarios.html', {
        'calendarios_e_datas': calendarios_e_datas,
        'form': form,
    })

# CRUD Calendarios: GET/PUT
@login_required(login_url='/login/')
def calendario_detail(request, id):
    if request.method == 'POST':
        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        form = CalendarioLetivoForm(request.POST, instance=calendario)

        if form.is_valid():
            form.save()
        
        return redirect('calendario_detail', id=id)

    calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
    return render(request, 'planner/calendarios/calendario_detail.html', {
        'calendario': calendario,
        'form': CalendarioLetivoForm(instance=calendario)
    })


# CRUD Calendarios: DELETE
@login_required(login_url='/login/')
def calendario_delete(request, id):
    if request.method == 'POST':
        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        calendario.delete()
        return redirect('calendarios')

# ############################################################################################################################
#                                                  Calendário Letivo + Datas Importantes
# ############################################################################################################################

# CRUD Datas Importantes: GET/POST
@login_required(login_url='/login/')
def calendario_datas_importantes(request, id):    
    calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)

    if request.method == 'POST':
        form = DataImportanteForm(request.POST)

        if form.is_valid():
            data_importante = form.save(commit=False)
            data_importante.calendario = calendario
            data_importante.save()
            return redirect('calendario_datas_importantes', id=id)
        
        else:
            messages.error(request, 'A data não está no intervalo do calendário')
            return render(request, 'planner/calendarios/calendario_datas_importantes.html', {
                'calendario': calendario,
                'form': form,
                'datas': calendario.datas.all().order_by('data')
            })
        
    return render(request, 'planner/calendarios/calendario_datas_importantes.html', {
        'calendario': calendario,
        'form': DataImportanteForm(),
        'periodo_form': PeriodoImportanteForm(),
        'datas': calendario.datas.all().order_by('data')
    })
        
# CRUD Datas Importantes: GET/PUT
@login_required(login_url='/login/')
def calendario_datas_importantes_detail(request, id, data_id):
    if request.method == 'POST':
        print('request ->', request.POST)

        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        data = get_object_or_404(DataImportante, id=data_id, calendario=calendario)
        form = DataImportanteForm(request.POST, instance=data)

        if form.is_valid():
            form.save()

        return redirect('calendario_datas_importantes', id=id)

# CRUD Datas Importantes: DELETE
@login_required(login_url='/login/')
def calendario_datas_importantes_delete(request, id, data_id):
    if request.method == 'POST':
        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        data = get_object_or_404(DataImportante, id=data_id, calendario=calendario)
        data.delete()

        return redirect('calendario_datas_importantes', id=id)


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
def avaliacao_detail(request, id):
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
def avaliacao_delete(request, id):
    if request.method == 'POST':
        avaliacao = get_object_or_404(Avaliacao, id=id, disciplina__user=request.user)
        avaliacao.delete()
        return redirect('avaliacoes')

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

# CRUD Tarefas: GET/PUT
@login_required(login_url='/login/')
def tarefa_detail(request, id):
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
def tarefa_delete(request, id):
    if request.method == 'POST':
        tarefa = get_object_or_404(Tarefa, id=id, disciplina__user=request.user)
        tarefa.delete()
        return redirect('tarefas')
    

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


# ############################################################################################################################
#                                                  Configurações
# ############################################################################################################################

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

@login_required(login_url='/login/')
def configuracoes_delete_view(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('submit_login')


# ############################################################################################################################
#                                                  Criar e Atualizar aulas/outras funções auxiliares
# ############################################################################################################################
def get_dias_aula_na_semana_disciplina(disciplina):
    """
    Obter os dias da semana de aual de uma disciplina
    """
    dias = set()
    for plano in disciplina.planos.all()[:5]:
        dia = get_dia_semana(plano.data)
        dias.add(dia)
    return dias


def get_dia_semana(proximo_dia):
    NAME_DAYS_WEEK = {
        'Monday': 'segunda',
        'Tuesday': 'terca',
        'Wednesday': 'quarta',
        'Thursday': 'quinta',
        'Friday': 'sexta',
        'Saturday': 'sábado',
        'Sunday': 'domingo'
    }

    dia_nome = calendar.day_name[proximo_dia.weekday()]
    return NAME_DAYS_WEEK[dia_nome]

def eh_possivel_carga_horaria(calendario, carga_horaria, dias_aulas, data_inicial, data_final):
    """
    Verifica se é possível cumprir a carga horária no período e dias informados
    """
    try:
        print("\n================ INÍCIO DEBUG: eh_possivel_carga_horaria ================\n")

        num_aulas = 0
        proximo_dia = data_inicial
        dias = dias_aulas.keys()

        # ---------------- VALIDAÇÕES ----------------
        print(">>> VALIDAÇÕES INICIAIS")
        print(f"Calendário recebido: {calendario}")
        print(f"Carga horária necessária: {carga_horaria}")
        print(f"Dias de aula informados: {dias_aulas}")
        print(f"Data inicial: {data_inicial}")
        print(f"Data final: {data_final}")

        if not calendario:
            raise ValueError('Calendário letivo não fornecido.')
        
        if not dias_aulas or len(dias_aulas) == 0:
            raise ValueError('Nenhum dia de aula especificado.')
        
        if data_inicial > data_final:
            raise ValueError('Data inicial não pode ser maior que data final.')
        
        if carga_horaria <= 0:
            raise ValueError('Carga horária deve ser maior que zero.')

        print("\n>>> PERÍODO E DIAS DE AULA")
        print(f"Período: {data_inicial:%d/%m/%Y} até {data_final:%d/%m/%Y}")
        print(f"Dias da semana com aula: {list(dias)}")

        # ---------------- CARREGAR DIAS NÃO LETIVOS ----------------
        print("\n>>> BUSCANDO DIAS NÃO LETIVOS...")
        try:
            dias_nao_letivos = set(
                DataImportante.objects.filter(calendario=calendario, dia_letivo=False)
                .values_list("data", flat=True)
            )
            print(f"{len(dias_nao_letivos)} dia(s) não letivo(s) encontrado(s).")
        except Exception as e:
            print(f"Erro ao buscar dias não letivos: {str(e)}")
            dias_nao_letivos = set()

        if dias_nao_letivos:
            print("\nDias NÃO LETIVOS:")
            for i, data in enumerate(sorted(dias_nao_letivos), 1):
                print(f"  {i}. {data:%d/%m/%Y}")
        else:
            print("Nenhum dia não letivo encontrado.")

        # ---------------- PROCESSAR AULAS ----------------
        print("\n>>> PROCESSANDO AULAS DIA A DIA")
        print("------------------------------------")

        while num_aulas < carga_horaria and proximo_dia <= data_final:
            dia_semana = get_dia_semana(proximo_dia)
            
            print(f"Data: {proximo_dia:%d/%m/%Y} ({dia_semana})", end="")

            if proximo_dia in dias_nao_letivos:
                print(" -> ❌ Não letivo")
            elif dia_semana not in dias:
                print(" -> ❌ Não é dia de aula")
            else:
                aulas_no_dia = int(dias_aulas.get(dia_semana, 0))
                print(f" -> Aula(s): {aulas_no_dia}")
                num_aulas += aulas_no_dia

            proximo_dia += timedelta(days=1)

        # ---------------- RESULTADO FINAL ----------------
        print("\n>>> RESULTADO FINAL")
        print(f"Aulas calculadas: {num_aulas}")
        print(f"Carga horária exigida: {carga_horaria}")
        print("\n================ FIM DEBUG ================\n")

        return num_aulas, carga_horaria

    except Exception as e:
        print("\n### ERRO ENCONTRADO ###")
        print(f"Erro em eh_possivel_carga_horaria: {str(e)}\n")
        raise Exception(f'Erro ao verificar se é possível cumprir a carga horária: {str(e)}')

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
            dias_nao_letivos = set(
                DataImportante.objects.filter(calendario=calendario, dia_letivo=False)
                .values_list("data", flat=True)
            )
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


def salvar_aulas_no_banco(disciplina, datas_aulas):
    """
    Salvar as aulas no banco de dados
    """
    try:
        for data, num_aulas in datas_aulas:
            PlanoAula.objects.create(
                disciplina=disciplina,
                data=data,
                titulo='Aula XX',
                num_aulas=num_aulas,
            )
    except Exception as e:
        print(f'Erro ao salvar aulas no banco: {str(e)}')
        raise Exception(f'Erro ao salvar as aulas no banco de dados: {str(e)}')


def gerar_aulas(disciplina, carga_horaria, dias_aulas, data_inicial=None):
    """
    Gera as aulas de uma disciplina
    """
    try:
        calendario = disciplina.calendario
        if data_inicial is None:
            data_inicial = calendario.data_inicio
        data_final = calendario.data_fim

        # Validações básicas
        if not calendario.data_inicio or not calendario.data_fim:
            raise ValueError('Calendário letivo não possui datas de início e fim definidas.')
        
        if calendario.data_inicio >= calendario.data_fim:
            raise ValueError('Data de início do calendário deve ser menor que a data de fim.')
        
        if not dias_aulas:
            raise ValueError('Nenhum dia de aula foi especificado.')
        
        if carga_horaria <= 0:
            raise ValueError('Carga horária deve ser maior que zero.')
        
        # print dados recebidos
        print(f'Calendario: {calendario}')
        print(f'carga_horaria: {carga_horaria}')
        print(f'dias_aulas: {dias_aulas}')
        print(f'data_inicial: {data_inicial}')
        print(f'data_final: {data_final}')

        datas_aulas = calcular_datas_aulas(
            calendario,
            carga_horaria,
            dias_aulas,
            data_inicial,
            data_final,
        )
        print('datas auls after return', datas_aulas)

        # ajustar as datas aqui das aulas existentes e salvar apenas as necessárias
        datas_aulas_filtradas = datas_aulas.copy()
        if disciplina.planos.all().count() > 0:
            index_proxima_data_adicionada = ajustar_datas_das_aulas(disciplina, datas_aulas, dias_aulas)
            datas_aulas_filtradas = datas_aulas_filtradas[index_proxima_data_adicionada:]

        # visualizar as aulas a serem salvas
        print(f'datas_aulas: {datas_aulas}')
        print('---- Datas pra serem salvas no banco ----')
        for i, (data, num_aulas) in enumerate(sorted(datas_aulas), 1):
            print(f'{i}. {data:%d/%m/%Y} ({num_aulas} aula(s))')
        
        # salvar no banco
        salvar_aulas_no_banco(disciplina, datas_aulas_filtradas)
        
    except Exception as e:
        print(f'Erro em gerar_aulas: {str(e)}')
        raise Exception(f'Erro ao gerar aulas: {str(e)}')

