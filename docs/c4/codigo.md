# Código

> Representado por diagramas UML para mostrar a implementação de classes


## Estrutura do projeto
```
professorhub/
├── docs/
│
├── professorhub/
│   ├── config/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── landing_page/
|   │   ├── migrations/
|   │   │   ├── __init__.py
│   │   ├── templates/
│   │   │   ├── landing_page/
│   │   │   │   ├── index.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   
│   ├── planner/
│   │   ├── management/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── limpar_registros_expirados.py
|   │   ├── migrations/
|   │   │   ├── __init__.py
│   │   ├── templates/
│   │   │   ├── planner/
│   │   │   │   ├── avaliacoes/
│   │   │   │   │   ├── avaliacoes.html
│   │   │   │   ├── calendarios/
│   │   │   │   │   ├── calendario_datas_importantes.html
│   │   │   │   │   ├── calendario_detail.html
│   │   │   │   │   ├── listar_calendarios.html
│   │   │   │   ├── disciplinas/
|   |   |   |   |   ├── disciplina_avaliacoes.html
|   |   |   |   |   ├── disciplina_configuracoes.html
|   |   |   |   |   ├── disciplina_ementas.html
|   |   |   |   |   ├── disciplina_objetivos.html
|   |   |   |   |   ├── disciplina_planos.html
|   |   |   |   |   ├── disciplina_tarefas.html
|   |   |   |   |   ├── disciplinas.html
│   │   │   │   ├── tarefas/
│   │   │   │   │   ├── tarefas.html
│   │   │   │   ├── admin_dashboard.html
│   │   │   │   ├── base.html
│   │   │   │   ├── configuracoes.html
│   │   │   ├── 404.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   
│   ├── teacher/
|   │   ├── migrations/
|   │   │   ├── __init__.py
│   │   ├── templates/
│   │   │   ├── teacher/
│   │   │   │   ├── ativar_conta.html
│   │   │   │   ├── base.html
│   │   │   │   ├── conta_ativada.html
│   │   │   │   ├── login.html
│   │   │   │   ├── recuperar-senha.html
│   │   │   │   ├── redefinir-senha.html
│   │   │   │   ├── register.html
│   │   │   │   ├── token_expirado.html
│   │   │   │   ├── validar-codigo.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │
│   └── static/
│       ├── css/
│       │   ├── base.css
│       │   ├── planner/
│       │   │   ├── base.css
│       │   │   └── dashboard.css
│       │   └── teacher/
│       │       └── base.css
│       │
│       └── js/
│           └── admin_dashboard.js
│           └── avaliacoes.js
│           └── base.js
│           └── calendario_datas_importantes.js
│           └── disciplina_detail_avaliacoes.js
│           └── disciplina_detail_configuracoes.js
│           └── disciplina_detail_planos.js
│           └── disciplina_detail_tarefas.js
│           └── disciplinas.js
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Explicação dos diretórios

| Diretório | Responsabilidade |
|---|---|
| `professorhub/` | Configurações do projeto Django |
| `landing_page/` | Paginas `landing page` |
| `teacher/` | Autenticação, cadastro e gerenciamento de docentes |
| `planner/` | Planejamento de aulas, disciplinas, tarefas e avaliações |
| `static/` | Arquivos CSS, JS e imagens |


## Pontos de atenção (To-do List)
- `limpar_registros_expirados.py`: implementar `jobs` no deploy e/ou `Celeris`
- `404.html`: revisar configuração para a exibição da página
- `services`: nao esquecer de reorganizar o codigo
- `validacoes`: nao esquecer de revisar as validacoes dos campos
- Reorganizar pasta `/static/js/` para:
    ```
        js/
        ├── planner/
        │   ├── calendario_datas_importantes.js
        |   ├── disciplina_detail_avaliacoes.js
        |   ├── disciplina_detail_configuracoes.js
        |   ├── disciplina_detail_planos.js
        |   ├── disciplina_detail_tarefas.js
        |   ├── disciplinas.js
        |   ├── avaliacoes.js
        │   ├── admin_dashboard.js
        ├──  base.js
    ```

