# ProfessorHub <br> Documentação do Software <br> Versão 2.0

## Introdução

### Finalidade
A proposta do software é otimizar e automatizar o planejamento acadêmico realizado por professores, centralizando em uma única plataforma a organização de disciplinas, conteúdos, atividades e calendário acadêmico.
    
O sistema busca reduzir tarefas maneuais, evitar inconsistências pedagógicas e facilitar toda a gestão das aulas. <br>

### Escopo
O aplicativo de software será uma plataforma completa para gestão de planejamento pedagógico, permitindo ao docente organizar disciplinas, criar e acompanhar conteúdos, registrar atividades, visualizar calendário acadêmico e manter todo o fluxo de planejamento centralizado.

O sistema  terá  como  escopo  fornecer  um  ambiente  robusto  que favoreça a padronização das aulas, diminua erros manuais e ofereça maior previsibilidade e controle no processo de ensino. 

### Definições, Acrônimos e Abreviações   
- **SUAP**: Sistema Unificado de Administração Pública 
- **HTML**: Hyper Text Markup Language 
- **CSS**: Cascading Style Sheets 
- **MVT**: Model View Template 
- **MVC**: Model View Controller

### Visão Geral
O planejamento docente é uma etapa fundamental para a organização do processo de ensino, porém muitas vezes é realizado de forma manual e fragmentada. Professores frequentemente enfrentam dificuldades relacionadas à sobrecarga de trabalho, falta de tempo e ausência de ferramentas centralizadas para organizar disciplinas, conteúdos e atividades.

Diante desse cenário, propõe-se o desenvolvimento do ProfessorHub, uma plataforma digital que auxilia na organização e no planejamento pedagógico. O sistema permitirá ao professor gerenciar disciplinas, estruturar conteúdos, registrar atividades e visualizar o calendário acadêmico de forma integrada.

## Descrição Geral

### Perspectiva do produto 
O ProfessorHub é um sistema web, acessível via navegador. 
Ele  faz  uso  de  um  banco  de  dados  para  armazenar  disciplinas, conteúdos e atividades, podendo futuramente integrar-se com serviços externos (como Google Classroom e/ou SUAP).
O sistema segue uma arquitetura baseada em módulos, facilitando a expansão futura. 
 
### Funções do produto 
- Gerenciar disciplinas (cadastrar, editar, excluir). 
- Criar e organizar conteúdos associados a uma disciplina. 
- Cadastrar atividades com datas, descrições e relação com conteúdos. 
- Exibir um calendário acadêmico visual com aulas e atividades. 
- Automatizar o planejamento/criação das aulas.  

### Características do usuário 
O sistema é voltado para os professores, visando facilitar e automatizar a organização de aulas e rotinas pedagógicas. 
 
### Restrições 
- O acesso será restrito mediante login e autenticação. 
- O sistema deve funcionar em navegadores 
- O sistema será utilizar as seguintes tecnologias:   
    - Django como framework principal no backend; 
    - PostgreSQL como banco de dados padrão par armazenamento das informações; 
    - HTML, CSS e JavaScript para a construção da interface;
    -  Bootstrap como framework de estilização e componentes 
visuais. 
- A plataforma deve ser responsiva para acesso via desktop ou mobile. 
 
### Suposições e dependências 
- O sistema deve ser acessível via web para permitir que os usuários acompanhem as operações de qualquer lugar. 
- Dependência de banco de dados para armazenamento das informações   
