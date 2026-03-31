from planner.models import CalendarioLetivo
from planner.forms import CalendarioLetivoForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date

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
def calendario_detail_view(request, id):
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
def calendario_delete_view(request, id):
    if request.method == 'POST':
        calendario = get_object_or_404(CalendarioLetivo, id=id, user=request.user)
        calendario.delete()
        return redirect('calendarios')
