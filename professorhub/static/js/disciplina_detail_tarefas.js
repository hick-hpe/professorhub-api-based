const formEditarTarefa = document.querySelector('#formEditarTarefa');
const modalEditarTarefa = document.querySelector('#modalEditarTarefa');
const listBtnEditarTarefa = document.querySelectorAll('.btnEditarTarefa');

listBtnEditarTarefa.forEach(btnEditarTarefa => {
    btnEditarTarefa.addEventListener('click', () => {
        const disciplina_id = btnEditarTarefa.getAttribute('data-disciplina')
        const tarefa_id = btnEditarTarefa.getAttribute('data-id')
        formEditarTarefa.action = `/disciplinas/${disciplina_id}/tarefas/${tarefa_id}/editar/`;
        
        const nome = btnEditarTarefa.getAttribute('data-nome');
        const descricao = btnEditarTarefa.getAttribute('data-descricao');
        const prazo = btnEditarTarefa.getAttribute('data-prazo');
        const status = btnEditarTarefa.getAttribute('data-status');

        document.querySelector('#nome_edit').value = nome;
        document.querySelector('#descricao_edit').textContent = descricao;
        document.querySelector('#prazo_edit').value = prazo;
        document.querySelector('#status_edit').value = status;
    });
});


const formExcluirTarefa = document.querySelector('#formExcluirTarefa');
const listBtnExcluirTarefa = document.querySelectorAll('.btnExcluirTarefa');
const nomeTarefaExcluir = document.querySelector('#nomeTarefaExcluir');

listBtnExcluirTarefa.forEach(btnExcluirTarefa => {
    btnExcluirTarefa.addEventListener('click', () => {
        const nome = btnExcluirTarefa.getAttribute('data-nome')
        const disciplina_id = btnExcluirTarefa.getAttribute('data-disciplina-id')
        const tarefa_id = btnExcluirTarefa.getAttribute('data-id')

        nomeTarefaExcluir.textContent = nome;
        formExcluirTarefa.action = `/disciplinas/${disciplina_id}/tarefas/${tarefa_id}/delete/`;
    });
});

