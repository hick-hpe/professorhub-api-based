
from django.shortcuts import render, redirect


def index(request):
    # return render(request,'landing_page/index.html') # desativada temporariamente
    return redirect('/login/') # redirecionar para '/login/' enquanto isso


