from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from planner.models import PeriodoImportante


# View Dashboard Admin
@login_required(login_url='/login/')
def admin_dashboard_view(request):
    data = {
        'periodos': PeriodoImportante.objects.filter(
            calendario__user=request.user
        )
    }
    return render(request, 'planner/admin_dashboard.html', data)