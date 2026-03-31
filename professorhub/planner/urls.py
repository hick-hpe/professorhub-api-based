from django.urls import path

# views - calendarios, datas importantes e períodos importantes
from planner.views.calendarios import (
    views_calendarios,
    views_calendarios_datas_importantes,
    views_calendario_periodos_importantes,
)

# views - disciplinas
from planner.views.disciplinas import (
    views_disciplinas,
    views_disciplinas_avaliacoes,
    views_disciplinas_configuracoes,
    views_disciplinas_tarefas,
    views_disciplina_planos,
    views_disciplina_ementas,
    views_disciplina_objetivos,
)

# views - geral
from planner.views.geral import (
    views_configuracoes,
    views_avaliacoes,
    views_tarefas,
    views_dashboard
)

# views - api json
from planner.views.api_json import view_json


urlpatterns = [
    # dashboard
    path('dashboard/', views_dashboard.admin_dashboard_view, name='admin_dashboard'),
    
    # obter todas as aulas
    path('planos/all/json/', view_json.listar_planos_json, name='planos_json'),
    
    # obter datas importantes do mês
    path('datas-importantes/mes-atual/<int:mes>/', view_json.datas_importantes_mes_json, name='datas_importantes_mes'),
    
    # tarefas
    path('tarefas/<int:id>/delete/', views_tarefas.tarefa_delete_view, name='tarefa_delete'),
    path('tarefas/<int:id>/', views_tarefas.tarefa_detail_view, name='tarefa_detail'),
    path('tarefas/mes-atual/<int:mes>/', views_tarefas.tarefas_mes_atual_view, name='tarefas_mes_atual'),
    path('tarefas/', views_tarefas.tarefas_view, name='tarefas'),

    # avaliações
    path('avaliacoes/<int:id>/delete/', views_avaliacoes.avaliacao_delete_view, name='avaliacao_delete'),
    path('avaliacoes/<int:id>/editar/', views_avaliacoes.avaliacao_detail_view, name='avaliacao_detail'),
    path('avaliacoes/', views_avaliacoes.avaliacoes_view, name='avaliacoes'),

    # disciplinas
    path('api/disciplinas/', views_disciplinas.disciplinas_api_view, name='disciplinas_api'),
    path('disciplinas/<int:id>/delete', views_disciplinas.disciplina_delete_view, name='disciplina_delete'),
    path('disciplinas/', views_disciplinas.disciplinas_view, name='disciplinas'),

    # disciplinas:planos
    path('disciplinas/<int:id>/planos/json/', views_disciplina_planos.disciplina_planos_json, name='disciplina_planos_json'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/editar', views_disciplina_planos.disciplina_planos_detail_view, name='editar_plano'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/excluir', views_disciplina_planos.disciplina_planos_excluir_view, name='disciplina_planos_excluir'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/trocar/<str:direction>', views_disciplina_planos.disciplina_planos_swap_view, name='disciplina_planos_swap'),
    path('disciplinas/<int:id>/planos/<int:plano_id>/duplicar', views_disciplina_planos.disciplina_planos_duplicar_view, name='disciplina_planos_duplicar'),
    path('disciplinas/<int:id>/planos/', views_disciplina_planos.disciplina_planos_view, name='disciplina_planos'),

    # disciplinas:tarefas
    path('disciplinas/<int:id>/tarefas/<int:atv_id>/editar/', views_disciplinas_tarefas.disciplina_tarefas_detail_view, name='disciplina_tarefas_editar'),
    path('disciplinas/<int:id>/tarefas/<int:atv_id>/delete/', views_disciplinas_tarefas.disciplina_tarefas_delete_view, name='disciplina_tarefas_delete'),
    path('disciplinas/<int:id>/tarefas/', views_disciplinas_tarefas.disciplina_tarefas_view, name='disciplina_tarefas'),
    
    # disciplinas:avaliacoes
    path('disciplinas/<int:id>/avaliacoes/<int:av_id>/editar/', views_disciplinas_avaliacoes.disciplina_avaliacao_detail_view, name='disciplina_avaliacao_detail'),
    path('disciplinas/<int:id>/avaliacoes/<int:av_id>/delete/', views_disciplinas_avaliacoes.disciplina_avaliacao_delete_view, name='disciplina_avaliacao_delete'),
    path('disciplinas/<int:id>/avaliacoes/', views_disciplinas_avaliacoes.disciplina_avaliacoes_view, name='disciplina_avaliacoes'),

    # disciplinas:configuracoes
    path('disciplinas/<int:id>/configuracoes/', views_disciplinas_configuracoes.disciplina_configuracoes_view, name='disciplina_configuracoes'),

    # disciplinas:ementas
    path('disciplinas/<int:id>/ementas/<int:ementa_id>/marcar/', views_disciplina_ementas.ementa_marcar_abordado_view, name='ementa_marcar_abordado'),
    path('disciplinas/<int:id>/ementas/<int:ementa_id>/editar/', views_disciplina_ementas.ementa_editar_view, name='ementa_editar'),
    path('disciplinas/<int:id>/ementas/<int:ementa_id>/excluir/', views_disciplina_ementas.ementa_excluir_view, name='ementa_excluir'),
    path('disciplinas/<int:id>/ementas/', views_disciplina_ementas.disciplina_ementas_view, name='disciplina_ementas'),

    # disciplinas:objetivos
    path('disciplinas/<int:id>/objetivos/<int:objetivo_id>/marcar/', views_disciplina_objetivos.objetivo_marcar_alcancado_view, name='objetivo_marcar_alcancado'),
    path('disciplinas/<int:id>/objetivos/<int:objetivo_id>/editar/', views_disciplina_objetivos.objetivo_editar_view, name='objetivo_editar'),
    path('disciplinas/<int:id>/objetivos/<int:objetivo_id>/excluir/', views_disciplina_objetivos.objetivo_excluir_view, name='objetivo_excluir'),
    path('disciplinas/<int:id>/objetivos/', views_disciplina_objetivos.disciplina_objetivos_view, name='disciplina_objetivos'),

    # configurações
    path('configuracoes/', views_configuracoes.configuracoes_view, name='configuracoes'),
    path('configuracoes/delete/', views_configuracoes.configuracoes_delete_view, name='configuracoes_delete'),

    # calendários
    path('calendarios/<int:id>/delete/', views_calendarios.calendario_delete_view, name='calendario_delete'),
    path('calendarios/<int:id>/', views_calendarios.calendario_detail_view, name='calendario_detail'),
    path('calendarios/', views_calendarios.calendarios_view, name='calendarios'),

    # datas importantes
    path('calendarios/<int:id>/datas-importantes/<int:data_id>/delete/', views_calendarios_datas_importantes.calendario_datas_importantes_delete_view, name='calendario_datas_importantes_delete'),
    path('calendarios/<int:id>/datas-importantes/<int:data_id>/', views_calendarios_datas_importantes.calendario_datas_importantes_detail_view, name='calendario_datas_importantes_detail'),
    path('calendarios/<int:id>/datas-importantes/', views_calendarios_datas_importantes.calendario_datas_importantes_view, name='calendario_datas_importantes'),

    # períodos importantes
    path('calendarios/<int:id>/periodos-importantes/', views_calendario_periodos_importantes.calendario_periodos_importantes_view, name='calendario_periodos_importantes'),
    path('calendarios/<int:id>/periodos-importantes/<int:periodo_id>/', views_calendario_periodos_importantes.calendario_periodos_importantes_detail_view, name='calendario_periodos_importantes_detail'),
    path('calendarios/<int:id>/periodos-importantes/<int:periodo_id>/delete/', views_calendario_periodos_importantes.calendario_periodos_importantes_delete_view, name='calendario_periodos_importantes_delete'),
]

