## Cadastrar Disciplinas
| UC01 | Descrição |
|------|-----------|
| Nome | Cadastrar Disciplinas |
| Descrição Geral | Permite que o docente cadastre disciplinas no sistema |
| Atores | Docente |
| Entrada | Nome, carga horária, dias das aulas, objetivos, ementa, período, calendário |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa a opção de cadastro de disciplina</li><li>Docente informa os dados da disciplina</li><li>Docente confirma o cadastro</li><li>Sistema valida os dados informados</li><li>Sistema registra a disciplina</li></ul> |
| Fluxos Alternativos | <ul><li>Campos obrigatórios não preenchidos: sistema solicita o preenchimento</li><li>Dados inválidos: sistema informa erro e solicita correção</li></ul> |
| Pós-condições | A disciplina é cadastrada no sistema e fica disponível para consulta, edição e geração de planos de aula |
| Prioridade | Alta |

## Editar dados da Disciplina
| UC05 | Descrição |
|------|-----------|
| Nome | Editar dados da Disciplina |
| Descrição Geral | Permite que o docente edite os dados de uma disciplina |
| Atores | Docente |
| Entrada | ID da disciplina, dados a serem alterados |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa disciplina existente</li><li>Docente altera os dados desejados</li><li>Docente confirma alterações</li><li>Sistema valida dados</li><li>Sistema atualiza disciplina</li></ul> |
| Fluxos Alternativos | <ul><li>Dados inválidos: sistema solicita correção</li></ul> |
| Pós-condições | Dados da disciplina atualizados |
| Prioridade | Alta |

## Excluir Disciplina
| UC06 | Descrição |
|------|-----------|
| Nome | Excluir Disciplina |
| Descrição Geral | Permite que o docente exclua uma disciplina |
| Atores | Docente |
| Entrada | Nome ou identificador da disciplina |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa disciplina</li><li>Docente seleciona opção excluir</li><li>Sistema solicita confirmação</li><li>Docente confirma exclusão</li><li>Sistema remove disciplina</li><li>Sistema redireciona para a tela da listagem das disciplina</li></ul> |
| Fluxos Alternativos | <ul><li>Docente cancela a operação: sistema mantém a disciplina</li></ul> |
| Pós-condições | Disciplina e componentes associados removidos |
| Prioridade | Alta |

## Gerar Aulas
| UC07 | Descrição |
|------|-----------|
| Nome | Gerar Aulas |
| Descrição Geral | Permite gerar automaticamente as datas das aulas de uma disciplina |
| Atores | Docente |
| Entrada | Disciplina, calendário |
| Fluxo Principal | <ul><li>Docente cria a disciplina</li><li>Sistema gera as aulas automaticamente</li><li>Sistema calcula datas conforme calendário</li><li>Sistema registra as aulas</li></ul> |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxos Alternativos | <ul><li>Calendário inválido: sistema informa erro</li></ul> |
| Pós-condições | Aulas geradas automaticamente |
| Prioridade | Alta |
