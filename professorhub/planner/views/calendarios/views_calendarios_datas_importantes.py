from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from planner.models import CalendarioLetivo, DataImportante
from planner.forms import DataImportanteForm, PeriodoImportanteForm
from planner.utils import evento_calendario_reajustar_datas_aulas_do_dia

# ############################################################################################################################
#                                                  Calendário Letivo: Datas Importantes
# ############################################################################################################################

# CRUD Datas Importantes: GET/POST
@login_required(login_url='/login/')
def calendario_datas_importantes_view(request, id):    
    calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)

    if request.method == 'POST':
        form = DataImportanteForm(request.POST)

        if form.is_valid():
            data_importante = form.save(commit=False)
            data_importante.calendario = calendario
            data_importante.save()
            # disparar 'evento' para reajustar datas de aulas
            mensagens_aulas = evento_calendario_reajustar_datas_aulas_do_dia(dia_que_disparou=data_importante)
            messages.warning(request, mensagens_aulas)
            return redirect('calendario_datas_importantes', id=id)
        
        else:
            return render(request, 'planner/calendarios/calendario_datas_importantes.html', {
                'calendario': calendario,
                'form': form,
                'periodo_form': PeriodoImportanteForm(),                
                'periodos': calendario.periodos.all().order_by('data_inicio'),
                'datas': calendario.datas.all().order_by('data')
            })
        
    return render(request, 'planner/calendarios/calendario_datas_importantes.html', {
        'calendario': calendario,
        'form': DataImportanteForm(),
        'periodo_form': PeriodoImportanteForm(),
        'datas': calendario.datas.all().order_by('data'),
        'periodos': calendario.periodos.all().order_by('data_inicio')
    })

        
# CRUD Datas Importantes: GET/PUT
@login_required(login_url='/login/')
def calendario_datas_importantes_detail_view(request, id, data_id):
    if request.method == 'POST':

        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        data_importante = get_object_or_404(DataImportante, id=data_id, calendario=calendario)
        dia_eh_letivo_antes = data_importante.dia_letivo
        form = DataImportanteForm(request.POST, instance=data_importante)
        dia_eh_letivo_depois = False

        if form.is_valid():
            form.save()
            dia_eh_letivo_depois = form.instance.dia_letivo
        
            # se houve mudança no status do dia (letivo / não letivo), reajustar as datas das aulas
            if dia_eh_letivo_antes != dia_eh_letivo_depois:
                mensagens_aulas = evento_calendario_reajustar_datas_aulas_do_dia(dia_que_disparou=data_importante)
                messages.warning(request, mensagens_aulas)

        # erros do form para o 'messages'
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(request, error)
                else:
                    messages.error(request, f'{form.fields[field].label}: {error}')
        return redirect('calendario_datas_importantes', id=id)


# CRUD Datas Importantes: DELETE
@login_required(login_url='/login/')
def calendario_datas_importantes_delete_view(request, id, data_id):
    if request.method == 'POST':
        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        data_importante = get_object_or_404(DataImportante, id=data_id, calendario=calendario)
        data_importante.delete()
        # disparar 'evento' para reajustar datas de aulas
        mensagens_aulas = evento_calendario_reajustar_datas_aulas_do_dia(dia_deletado=True)
        messages.warning(request, mensagens_aulas)
        return redirect('calendario_datas_importantes', id=id)

