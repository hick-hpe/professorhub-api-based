## Cadastrar Tarefas
| UC03 | Descrição |
|------|-----------|
| Nome | Cadastrar Tarefas |
| Descrição Geral | Permite que o docente cadastre tarefas no sistema |
| Atores | Docente |
| Entrada | Nome, prazo, tipo |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa a opção de cadastro de tarefa</li><li>Docente informa os dados da tarefa</li><li>Docente confirma o cadastro</li><li>Sistema valida os dados</li><li>Sistema registra a tarefa</li></ul> |
| Fluxos Alternativos | <ul><li>Campos obrigatórios não preenchidos: sistema solicita preenchimento</li><li>Dados inválidos: sistema informa erro</li></ul> |
| Pós-condições | Tarefa cadastrada no sistema |
| Prioridade | Alta |

## Editar dados da Tarefa
| UC08 | Descrição |
|------|-----------|
| Nome | Editar dados da Tarefa |
| Descrição Geral | Permite que o docente edite os dados de uma tarefa |
| Atores | Docente |
| Entrada | ID da tarefa, dados a serem alterados |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa a lista de tarefas</li><li>Docente seleciona a tarefa desejada</li><li>Docente altera os dados da tarefa</li><li>Docente confirma as alterações</li><li>Sistema valida os dados informados</li><li>Sistema atualiza a tarefa</li></ul> |
| Fluxos Alternativos | <ul><li>Dados inválidos: sistema informa erro e solicita correção</li><li>Docente cancela a edição: sistema mantém os dados anteriores</li></ul> |
| Pós-condições | Dados da tarefa atualizados |
| Prioridade | Alta |

## Excluir Tarefa
| UC12 | Descrição |
|------|-----------|
| Nome | Excluir Tarefa |
| Descrição Geral | Permite que o docente exclua uma tarefa |
| Atores | Docente |
| Entrada | ID da tarefa |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa a lista de tarefas</li><li>Docente seleciona a tarefa que deseja excluir</li><li>Sistema solicita confirmação da exclusão</li><li>Docente confirma a exclusão</li><li>Sistema remove a tarefa do sistema</li></ul> |
| Fluxos Alternativos | <ul><li>Docente cancela a exclusão: sistema mantém a tarefa</li></ul> |
| Pós-condições | Tarefa excluída do sistema |
| Prioridade | Média |