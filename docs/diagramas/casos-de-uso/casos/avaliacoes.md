## Cadastrar Avaliações
| UC02 | Descrição |
|------|-----------|
| Nome | Cadastrar Avaliações |
| Descrição Geral | Permite que o docente cadastre avaliações no sistema |
| Atores | Docente |
| Entrada | Nome, prazo, tipo |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa a opção de cadastro de avaliação</li><li>Docente informa os dados da avaliação</li><li>Docente confirma o cadastro</li><li>Sistema valida os dados</li><li>Sistema registra a avaliação</li></ul> |
| Fluxos Alternativos | <ul><li>Campos obrigatórios não preenchidos: sistema solicita preenchimento</li><li>Dados inválidos: sistema informa erro</li></ul> |
| Pós-condições | Avaliação cadastrada no sistema |
| Prioridade | Alta |

## Editar dados da Avaliação
| UC09 | Descrição |
|------|-----------|
| Nome | Editar dados da Avaliação |
| Descrição Geral | Permite que o docente edite os dados de uma avaliação |
| Atores | Docente |
| Entrada | ID da avaliação, dados a serem alterados |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa a lista de avaliações</li><li>Docente seleciona a avaliação desejada</li><li>Docente altera os dados da avaliação</li><li>Docente confirma as alterações</li><li>Sistema valida os dados informados</li><li>Sistema atualiza a avaliação</li></ul> |
| Fluxos Alternativos | <ul><li>Dados inválidos: sistema informa erro e solicita correção</li><li>Docente cancela a edição: sistema mantém os dados anteriores</li></ul> |
| Pós-condições | Dados da avaliação atualizados |
| Prioridade | Alta |

## Excluir Avaliação
| UC10 | Descrição |
|------|-----------|
| Nome | Excluir Avaliação |
| Descrição Geral | Permite que o docente exclua uma avaliação |
| Atores | Docente |
| Entrada | ID da avaliação |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul><li>Docente acessa a lista de avaliações</li><li>Docente seleciona a avaliação que deseja excluir</li><li>Sistema solicita confirmação da exclusão</li><li>Docente confirma a exclusão</li><li>Sistema remove a avaliação do sistema</li></ul> |
| Fluxos Alternativos | <ul><li>Docente cancela a exclusão: sistema mantém a avaliação</li></ul> |
| Pós-condições | Avaliação excluída do sistema |
| Prioridade | Média |
