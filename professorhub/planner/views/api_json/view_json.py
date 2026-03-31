from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from planner.models import PlanoAula
from django.utils import timezone
from planner.models import DataImportante


# AJAX: GET todos os planos de aulas
@login_required(login_url='/login/')
def listar_planos_json(request):
    planos = PlanoAula.objects.filter(disciplina__user=request.user).order_by('data')
    return JsonResponse({
        'planos': list(planos.values('id', 'titulo', 'data', 'disciplina__nome', 'status'))
    })


# AJAX: GET datas importantes do mês
@login_required(login_url='/login/')
def datas_importantes_mes_json(request, mes):
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

