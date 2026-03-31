from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from planner.models import CalendarioLetivo
from planner.forms import DataImportanteForm, PeriodoImportanteForm
from planner.models import PeriodoImportante

# ############################################################################################################################
#                                                  Calendário Letivo: Periodos Importantes
# ############################################################################################################################

# CRUD Periodos Importantes: GET/POST
@login_required(login_url='/login/')
def calendario_periodos_importantes_view(request, id):
    calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)

    if request.method == 'POST':
        form = PeriodoImportanteForm(request.POST)

        if form.is_valid():
            periodo_importante = form.save(commit=False)
            periodo_importante.calendario = calendario
            periodo_importante.save()
            return redirect('calendario_datas_importantes', id=id)
        
        else:
            print('--- Houve um erro ao salvar o período importante. ----')
            print(form.errors)
            # messages.error(request, 'Houve um erro ao salvar o período importante.')
            return render(request, 'planner/calendarios/calendario_datas_importantes.html', {
                'calendario': calendario,
                'form': DataImportanteForm(),
                'periodo_form': form,
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

# CRUD Periodos Importantes: GET/PUT
@login_required(login_url='/login/')
def calendario_periodos_importantes_detail_view(request, id, periodo_id):
    if request.method == 'POST':
        print('request ->', request.POST)

        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        periodo = get_object_or_404(PeriodoImportante, id=periodo_id, calendario=calendario)
        form = PeriodoImportanteForm(request.POST, instance=periodo)

        if form.is_valid():
            form.save()
        else:
            print('---- errors ----')
            print(form.errors)        

        return redirect('calendario_datas_importantes', id=id)

# CRUD Periodos Importantes: DELETE
@login_required(login_url='/login/')
def calendario_periodos_importantes_delete_view(request, id, periodo_id):
    if request.method == 'POST':
        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        periodo = get_object_or_404(PeriodoImportante, id=periodo_id, calendario=calendario)
        periodo.delete()

        return redirect('calendario_datas_importantes', id=id)
