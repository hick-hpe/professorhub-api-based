from django.urls import path
from .views import *

urlpatterns = [
    # # dashboard
    path('dashboard/', admin_dashboard_view, name='admin_dashboard'),
    
    # obter todas as aulas
    path('planos/all/json/', planos_json, name='planos_json'),
    
    # obter datas importantes do mês
    path('datas-importantes/mes-atual/<int:mes>/', datas_importantes_mes_view, name='datas_importantes_mes'),
    
    # # tarefas
    path('tarefas/<int:id>/delete/', tarefa_delete, name='tarefa_delete'),
    path('tarefas/<int:id>/', tarefa_detail, name='tarefa_detail'),
    path('tarefas/mes-atual/<int:mes>/', tarefas_mes_atual_view, name='tarefas_mes_atual'),
    path('tarefas/', tarefas_view, name='tarefas'),

    # # avaliações
    path('avaliacoes/<int:id>/delete/', avaliacao_delete, name='avaliacao_delete'),
    path('avaliacoes/<int:id>/editar/', avaliacao_detail, name='avaliacao_detail'),
    path('avaliacoes/', avaliacoes_view, name='avaliacoes'),

    # # disciplinas
    path('disciplinas/<int:id>/delete', disciplina_delete, name='disciplina_delete'),
    path('disciplinas/', disciplinas_view, name='disciplinas'),

    # disciplinas:planos
    path('disciplinas/<int:id>/planos/json/', disciplina_planos_json, name='disciplina_planos_json'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/editar', disciplina_planos_detail, name='editar_plano'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/excluir', disciplina_planos_excluir, name='disciplina_planos_excluir'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/trocar/<str:direction>', disciplina_planos_swap, name='disciplina_planos_swap'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/duplicar', disciplina_planos_duplicar, name='disciplina_planos_duplicar'),
    path('disciplinas/<int:id>/planos/', disciplina_planos, name='disciplina_planos'),

    # # disciplinas:tarefas
    path('disciplinas/<int:id>/tarefas/<int:atv_id>/editar/', disciplina_tarefas_detail, name='disciplina_tarefas_editar'),
    path('disciplinas/<int:id>/tarefas/<int:atv_id>/delete/', disciplina_tarefas_delete, name='disciplina_tarefas_delete'),
    path('disciplinas/<int:id>/tarefas/', disciplina_tarefas, name='disciplina_tarefas'),
    
    # # disciplinas:avaliacoes
    path('disciplinas/<int:id>/avaliacoes/<int:av_id>/editar/', disciplina_avaliacao_detail, name='disciplina_avaliacao_detail'),
    path('disciplinas/<int:id>/avaliacoes/<int:av_id>/delete/', disciplina_avaliacao_delete, name='disciplina_avaliacao_delete'),
    path('disciplinas/<int:id>/avaliacoes/', disciplina_avaliacoes, name='disciplina_avaliacoes'),

    # # disciplinas:configuracoes
    path('disciplinas/<int:id>/configuracoes/', disciplina_configuracoes, name='disciplina_configuracoes'),

    # # disciplinas:ementas
    path('disciplinas/<int:id>/ementas/<int:ementa_id>/marcar/', ementa_marcar_abordado, name='ementa_marcar_abordado'),
    path('disciplinas/<int:id>/ementas/<int:ementa_id>/editar/', ementa_editar, name='ementa_editar'),
    path('disciplinas/<int:id>/ementas/<int:ementa_id>/excluir/', ementa_excluir, name='ementa_excluir'),
    path('disciplinas/<int:id>/ementas/', disciplina_ementas, name='disciplina_ementas'),

    # # disciplinas:objetivos
    path('disciplinas/<int:id>/objetivos/<int:objetivo_id>/marcar/', objetivo_marcar_alcancado, name='objetivo_marcar_alcancado'),
    path('disciplinas/<int:id>/objetivos/<int:objetivo_id>/editar/', objetivo_editar, name='objetivo_editar'),
    path('disciplinas/<int:id>/objetivos/<int:objetivo_id>/excluir/', objetivo_excluir, name='objetivo_excluir'),
    path('disciplinas/<int:id>/objetivos/', disciplina_objetivos, name='disciplina_objetivos'),

    # # configurações
    path('configuracoes/', configuracoes_view, name='configuracoes'),
    path('configuracoes/delete/', configuracoes_delete_view, name='configuracoes_delete'),

    # # calendários
    path('calendarios/<int:id>/delete/', calendario_delete, name='calendario_delete'),
    path('calendarios/<int:id>/', calendario_detail, name='calendario_detail'),
    path('calendarios/', calendarios_view, name='calendarios'),

    # datas importantes
    path('calendarios/<int:id>/datas-importantes/<int:data_id>/delete/', calendario_datas_importantes_delete, name='calendario_datas_importantes_delete'),
    path('calendarios/<int:id>/datas-importantes/<int:data_id>/', calendario_datas_importantes_detail, name='calendario_datas_importantes_detail'),
    path('calendarios/<int:id>/datas-importantes/', calendario_datas_importantes, name='calendario_datas_importantes'),

    # períodos importantes
    path('calendarios/<int:id>/periodos-importantes/', calendario_periodos_importantes, name='calendario_periodos_importantes'),
    path('calendarios/<int:id>/periodos-importantes/<int:periodo_id>/', calendario_periodos_importantes_detail, name='calendario_periodos_importantes_detail'),
    path('calendarios/<int:id>/periodos-importantes/<int:periodo_id>/delete/', calendario_periodos_importantes_delete, name='calendario_periodos_importantes_delete'),
]
