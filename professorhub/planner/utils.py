from django.db.models import Sum
from planner.models import DataImportante, Disciplina, PlanoAula, PeriodoImportante
import calendar
from datetime import timedelta

# ############################################################################################################################
#                            Criar e Atualizar aulas/outras funções auxiliares
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


# obter nome do dia da semana a partir de uma data
def get_dia_semana(data):
    NAME_DAYS_WEEK = {
        'Monday': 'segunda',
        'Tuesday': 'terca',
        'Wednesday': 'quarta',
        'Thursday': 'quinta',
        'Friday': 'sexta',
        'Saturday': 'sábado',
        'Sunday': 'domingo'
    }

    dia_nome = calendar.day_name[data.weekday()]
    return NAME_DAYS_WEEK[dia_nome]
    

# obter os dias da semana de aula de uma disciplina
def get_dias_aula_na_semana_disciplina(disciplina):
    """
    Obter os dias da semana de aula de uma disciplina
    """
    dias = set()
    for plano in disciplina.planos.all()[:5]:
        dia = get_dia_semana(plano.data)
        dias.add(dia)
    return dias


# verificar se é possível cumprir a carga horária no período e dias informados
def eh_possivel_carga_horaria(calendario, carga_horaria, dias_aulas, data_inicial, data_final):
    """
    Verifica se é possível cumprir a carga horária no período e dias informados
    """
    try:
        print("\n================ INÍCIO DEBUG: 'eh_possivel_carga_horaria' ================\n")

        num_aulas = 0
        proximo_dia = data_inicial
        dias = dias_aulas.keys()

        # ---------------- VALIDAÇÕES ----------------
        print(">>> VALIDAÇÕES INICIAIS")
        print(f"Calendário recebido: {calendario}")
        print(f"Carga horária necessária: {carga_horaria}")
        print(f"Dias de aula informados: {dias_aulas}")
        print(f"Data inicial: {data_inicial:%d/%m/%Y}")
        print(f"Data final: {data_final:%d/%m/%Y}")

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


# gerar as aulas de uma disciplina
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


# salvar as aulas no banco de dados
def salvar_aulas_no_banco(disciplina, datas_aulas):
    """
    Salvar as aulas no banco de dados
    """
    try:
        contador = (disciplina.planos.count()) + 1
        for data, num_aulas in datas_aulas:
            PlanoAula.objects.create(
                disciplina=disciplina,
                data=data,
                titulo=f'Aula {contador:02}',
                num_aulas=num_aulas,
            )
            contador += 1
    except Exception as e:
        print(f'Erro ao salvar aulas no banco: {str(e)}')
        raise Exception(f'Erro ao salvar as aulas no banco de dados: {str(e)}')


# obter o número de aulas por dia da semana de uma disciplina
def num_aulas_por_dia_disciplina(disciplina, tirar_dias_zerados=True):
    """
    Obter o número de aulas por dia da semana de uma disciplina
    """
    dias_aulas = {
        'segunda': 0,
        'terca': 0,
        'quarta': 0,
        'quinta': 0,
        'sexta': 0,
        # 'sábado': 0 # rever sabados letivos
    }
    for plano in disciplina.planos.all()[:5]:
        dia = get_dia_semana(plano.data)
        dias_aulas[dia] = plano.num_aulas

    if tirar_dias_zerados:
        # remove os dias que não são de aula (com 0 aulas)
        dias_aulas = {dia: num for dia, num in dias_aulas.items() if num != 0}

    return dias_aulas


# verifica se uma data é dia letivo para a disciplina
def eh_dia_letivo(data, dias_aulas_disciplinas):
    dia_semana = get_dia_semana(data)

    # verificar se a data é um dia de aula da disciplina
    eh_data_importante_nao_letiva = DataImportante.objects.filter(
        data=data, dia_letivo=False
    ).first()

    # verificar se a data faz parte de um período importante não letivo (ex: férias, recesso, etc)
    periodo_importante_nao_letivo = PeriodoImportante.objects.filter(
        data_inicio__lte=data, data_fim__gte=data, dia_letivo=False
    ).first()

    # verificar se o dia da semana é um dia de aula da disciplina e não é um dia importante não letivo
    return (
        dia_semana in dias_aulas_disciplinas
        and not eh_data_importante_nao_letiva
        and not periodo_importante_nao_letivo
    )


# organizar o dia de aulas por dia na semana de uma disciplina
def criar_obj_num_aulas_por_dia_disciplina(disciplina):
    dias_aulas = {}
    planos_aulas = disciplina.planos.all()[:5]
    
    for plano in planos_aulas:
        dia = get_dia_semana(plano.data)
        num = plano.num_aulas
        dias_aulas[dia] = num

    return dias_aulas


# evento: reajustar datas das aulas ao criar/atualizar/excluir uma data importante
def evento_calendario_reajustar_datas_aulas_do_dia(
    dia_que_disparou: DataImportante | None = None,
    dia_deletado: bool = False
):
    """
    Evento que reajusta as datas das aulas quando um dia importante no calendário letivo é criado/atualizado/excluído
    """
    
    # obter calendario
    calendario = dia_que_disparou.calendario

    # obter disciplinas associadas ao calendário
    disciplinas = Disciplina.objects.filter(calendario=calendario)
    
    if dia_que_disparou is not None:

        for disciplina in disciplinas:
            # obter dias de aula da disciplina
            dias_aulas_disciplinas = get_dias_aula_na_semana_disciplina(disciplina)

            # verificar se é possível dentro da carga horaria da disciplina
            dia_aulas = criar_obj_num_aulas_por_dia_disciplina(disciplina)
            num_aulas, carga_horaria = eh_possivel_carga_horaria(
                calendario,
                disciplina.carga_horaria,
                dia_aulas,
                calendario.data_inicio,
                calendario.data_fim
            )
            eh_possivel_cumprir = (num_aulas >= carga_horaria)
            if not eh_possivel_cumprir:
                # ===============================
                # REFACTOR: 
                # add modelo 'NumAulasPorDiaDisiciplina'
                # - disiciplina: FK
                # - plano_aula: FK
                # - num_aulas
                # - dia_da_semana
                # ===============================
                # obter ultimo dia de aula
                ultima_aula = disciplina.planos.order_by('data').last()
                if not ultima_aula:
                    continue

                # obter o proximo dia letivo de aula
                proxima_dia_aula = proximo_dia_letivo(ultima_aula.data, get_dias_aula_na_semana_disciplina(disciplina))

                # primeiro plano de aula neste dia da semana                
                django_week_day = ((proxima_dia_aula.weekday() + 1) % 7) + 1

                plano_aula = disciplina.planos.filter(
                    data__week_day=django_week_day
                ).first()

                if not plano_aula:
                    continue

                # aulas neste dia
                aulas_faltantes = plano_aula.num_aulas

                # aviso apenas
                mensagem = f"Faltam {aulas_faltantes} aula{'s' if aulas_faltantes != 1 else ''} para cumprir a carga horária!"
                print(f'>_ AVISSOOO ({disciplina.nome}): {mensagem}')
                disciplina.aviso = mensagem
                disciplina.save()

                return mensagem

            # se tornou 'não letivo'
            elif not dia_que_disparou.dia_letivo:
                # verificar se disciplina possui aula no dia 'dia_que_disparou'
                planos_no_dia = disciplina.planos.filter(data=dia_que_disparou.data)

                # se possuir, recalcular as datas das aulas a partir dessa data
                if planos_no_dia.exists():
                    # movendo as aulas para frente
                    reajustar_datas_aulas_para_frente(disciplina, dia_que_disparou, dias_aulas_disciplinas)
                
                return ''
        
            # se tornou 'letivo'
            elif dia_que_disparou.dia_letivo or dia_deletado:
                # verificar se a disciplina possui aulas neste dia da semana
                # se tiver, atualizar os dias
                # senão, não fazer nada
                dia_semana_dia_mudado = get_dia_semana(dia_que_disparou.data)

                if dia_semana_dia_mudado in dias_aulas_disciplinas:
                    # movendo as aulas para trás
                    reajustar_datas_aulas_para_tras(disciplina, dia_que_disparou, dias_aulas_disciplinas)

                return ''


# proximo dia letivo para a disciplina
def proximo_dia_letivo(data, dias_aulas_disciplinas):
    proximo_dia = data + timedelta(days=1)
    while not eh_dia_letivo(proximo_dia, dias_aulas_disciplinas):
        proximo_dia += timedelta(days=1)
    return proximo_dia


# mover as aulas para frente (próximo dia letivo)
def reajustar_datas_aulas_para_tras(
    disciplina,
    data_importante,
    dias_aulas_disciplinas
):
    """
    Move as aulas para trás (dia letivo anterior)
    quando uma data importante alterna para 'letivo'.
    """

    planos_aulas = (
        disciplina.planos
        .filter(data__gte=data_importante.data)
        .order_by('data')
    )

    ultimo_dia_ocupado = data_importante.data - timedelta(days=1)

    for plano in planos_aulas:
        nova_data = proximo_dia_letivo(
            ultimo_dia_ocupado,
            dias_aulas_disciplinas
        )
        plano.data = nova_data
        plano.save()

        ultimo_dia_ocupado = nova_data


# mover as datas das aulas para um dia letivo se uma data importante for alterada para 'letivo'
def reajustar_datas_aulas_para_frente(
    disciplina,
    data_importante,
    dias_aulas_disciplinas
):
    """
    Move as aulas para trás (dia letivo anterior) ou para frente (dia letivo posterior)
    quando uma data importante alterna entre letiva e não letiva.
    """

    planos_aulas = (
        disciplina.planos
        .filter(data__gte=data_importante.data)
        .order_by('data')
    )
    print(f'--- Reajustando datas das aulas da disciplina "{disciplina.nome}": {disciplina.planos.count()} ao todo ---')

    lista_dias = []
    for plano in planos_aulas:
        lista_dias.append(plano.data.strftime('%d/%m/%Y'))
    print(f'Dias atuais de aulas: {lista_dias}')

    # 'ultimo_dia_ocupado' é o dia da data importante, entao busca o próximo dia letivo a partir dele
    ultimo_dia_ocupado = data_importante.data

    for plano in planos_aulas:
        nova_data = plano.data + timedelta(days=1)

        # procura o dia letivo anterior válido
        nova_data = proximo_dia_letivo(ultimo_dia_ocupado, dias_aulas_disciplinas)

        # atualiza a aula
        plano.data = nova_data
        plano.save()

        # atualiza o último dia ocupado
        ultimo_dia_ocupado = nova_data


# ajustar as datas das aulas a partir de uma data
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


# Evento: Reajustar datas das aulas ao criar/atualizar/excluir um período importante
# def evento_calendario_reajustar_datas_aulas_do_periodo(
#     periodo_que_disparou: PeriodoImportante | None = None,
#     periodos_inicial: tuple | None = None,
#     periodos_atual: tuple | None = None,
#     periodo_deletado: bool = False,
# ):
#     """
#     Evento que reajusta as datas das aulas quando um período importante no calendário letivo é criado/atualizado/excluído
#     """
    
#     # obter calendario
#     calendario = periodo_que_disparou.calendario

#     # obter disciplinas associadas ao calendário
#     disciplinas = Disciplina.objects.filter(calendario=calendario)

#     if periodo_que_disparou is not None:
#         # todo: implementar reajuste por período importante
#         for disciplina in disciplinas:
#             # ativar o periodo atual

#             # mudar as datas
#             pass
