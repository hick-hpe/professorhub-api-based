# ProfessorHub

## Cadastro de Docentes

| UC01 | Descrição |
|-----|-----------|
| Nome | Cadastro de Docentes |
| Descrição Geral | Permite que o docente crie uma conta no sistema |
| Atores | Docente |
| Entrada | Nome de usuário, email e senha |
| Pré-condições | O docente deve ter acesso ao sistema e preencher os dados obrigatórios |
| Fluxo Principal | <ul> <li>Docente acessa a tela de cadastro</li> <li>Docente informa nome de usuário, email e senha</li> <li>Docente confirma o cadastro</li> <li>Sistema valida os dados informados</li> <li>Sistema cria a conta do docente</li> </ul> |
| Fluxos Alternativos | <ul> <li>Email já cadastrado: Sistema informa erro e solicita outro email</li> <li>UC00s obrigatórios não preenchidos: Sistema solicita o preenchimento</li> <li>Senha inválida: Sistema informa os requisitos da senha</li> </ul> |
| Pós-condições | O docente está logado e pode acessar as funcionalidades do sistema |
| Prioridade | Alta |


## Login de Docentes
| UC00               | Descrição |
|--------------------|-----------|
| Nome | Login de Docentes |
| Descrição Geral | Permite que o docente crie uma conta e realize login para acessar o sistema |
| Atores | Docente |
| Entrada | Email e senha |
| Pré-condições | O docente deve ter acesso ao sistema e preencher os dados obrigatórios |
| Fluxo Principal | <ul> <li>Docente acessa a tela de login</li> <li>Docente informa email e senha</li> <li>Docente confirma o login</li> <li>Sistema valida as credenciais</li> <li>Sistema permite acesso ao sistema</li> </ul> |
| Fluxos Alternativos | <ul> <li>Email ou senha incorretos: Sistema exibe mensagem de erro</li> <li>UC00s vazios: Sistema solicita o preenchimento</li> <li>Conta inexistente: Sistema sugere cadastro</li> </ul> |
| Pós-condições | O docente está logado e pode acessar as funcionalidades do sistema |
| Prioridade | Alta |


## Editar dados da Conta
| UC00               | Descrição |
|--------------------|-----------|
| Nome | Editar dados da Conta |
| Descrição Geral | Permite que o docente edite os dados de sua conta |
| Atores | Docente |
| Entrada | Nome de usuário, email e senha |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul> <li>Docente acessa a área de configurações da conta</li> <li>Docente altera os dados desejados</li> <li>Docente confirma as alterações</li> <li>Sistema valida os novos dados</li> <li>Sistema atualiza as informações da conta</li> </ul> |
| Fluxos Alternativos | <ul> <li>Email já utilizado: Sistema solicita outro email</li> <li>Dados inválidos: Sistema informa erro e pede correção</li> <li>Docente cancela a edição: Nenhuma alteração é salva</li> </ul> |
| Pós-condições | Os dados da conta são atualizados com sucesso |
| Prioridade | Média |


## Excluir Conta
| UC00               | Descrição |
|--------------------|-----------|
| Nome | Excluir Conta |
| Descrição Geral | Permite que o docente exclua sua conta |
| Atores | Docente |
| Entrada | Confirmação de exclusão (sim/não) |
| Pré-condições | O docente deve estar logado no sistema |
| Fluxo Principal | <ul> <li>Docente acessa a opção excluir conta</li> <li>Sistema solicita confirmação</li> <li>Docente confirma a exclusão</li> <li>Sistema remove os dados da conta</li> <li>Sistema redireciona o usuário para a tela de login</li> </ul> |
| Fluxos Alternativos | <ul> <li>Docente cancela a exclusão: Conta permanece ativa</li> </ul> |
| Pós-condições | A conta é deletada e o usuário é direcionado para a tela de login |
| Prioridade | Baixa/Média |


## Recuperação de conta
| UC00               | Descrição |
|--------------------|-----------|
| Nome | Recuperação de conta |
| Descrição Geral | Permite que o docente solicite a recuperação de sua conta |
| Atores | Docente |
| Entrada | E-mail cadastrado |
| Pré-condições | O docente deve possuir uma conta registrada no sistema |
| Fluxo Principal | <ul> <li>Docente acessa a opção "Esqueci minha senha"</li> <li>Docente informa o e-mail cadastrado</li> <li>Sistema verifica se o e-mail existe</li> <li>Sistema gera um código de verificação</li> <li>Sistema envia o código para o e-mail do docente</li> </ul> |
| Fluxos Alternativos | <ul> <li>Email não cadastrado: Sistema informa erro</li> <li>Falha no envio do email: Sistema solicita nova tentativa</li> </ul> |
| Pós-condições | Um código de verificação é enviado para o e-mail do docente |
| Prioridade | Média |


## Redefinir senha
| UC00               | Descrição |
|--------------------|-----------|
| Nome | Redefinir senha |
| Descrição Geral | Permite que o docente redefina sua senha utilizando um código de verificação enviado por e-mail |
| Atores | Docente |
| Entrada | Código de verificação recebido por e-mail e nova senha |
| Pré-condições | O docente deve ter solicitado a recuperação de conta e possuir o código válido |
| Fluxo Principal | <ul> <li>Docente acessa a tela de redefinição de senha</li> <li>Docente informa o código de verificação</li> <li>Docente informa a nova senha</li> <li>Sistema valida o código</li> <li>Sistema atualiza a senha da conta</li> </ul> |
| Fluxos Alternativos | <ul> <li>Código inválido ou expirado: Sistema solicita novo código</li> <li>Senha não atende aos requisitos: Sistema solicita nova senha</li> </ul> |
| Pós-condições | A senha do docente é atualizada com sucesso e ele pode acessar o sistema |
| Prioridade | Média |

