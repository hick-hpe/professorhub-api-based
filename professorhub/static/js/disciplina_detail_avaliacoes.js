const formEditarAvaliacao = document.querySelector('#formEditarAvaliacao');
const modalEditarAvaliacao = document.querySelector('#modalEditarAvaliacao');
const listBtnEditarAvaliacao = document.querySelectorAll('.btnEditarAvaliacao');

listBtnEditarAvaliacao.forEach(btnEditarAvaliacao => {
    btnEditarAvaliacao.addEventListener('click', () => {
        const disciplina_id = btnEditarAvaliacao.getAttribute('data-disciplina')
        const avaliacao_id = btnEditarAvaliacao.getAttribute('data-id')
        formEditarAvaliacao.action = `/disciplinas/${disciplina_id}/avaliacoes/${avaliacao_id}/editar/`;
        
        console.log('disciplina_id:', disciplina_id);
        const identificador = btnEditarAvaliacao.getAttribute('data-identificador');
        const plano_aula = btnEditarAvaliacao.getAttribute('data-plano-aula');
        const tipo = btnEditarAvaliacao.getAttribute('data-tipo');
        const status = btnEditarAvaliacao.getAttribute('data-status');
        const data = btnEditarAvaliacao.getAttribute('data-data');
        const etapa = btnEditarAvaliacao.getAttribute('data-etapa');

        document.querySelector('#identificador_edit').value = identificador;
        document.querySelector('#disciplina_edit').value = disciplina_id;
        document.querySelector('#plano_aula_edit').value = plano_aula;
        document.querySelector('#tipo_edit').value = tipo;
        document.querySelector('#status_edit').value = status;
        document.querySelector('#data_edit').value = data;
        document.querySelector('#etapa_edit').value = etapa;
    });
});


const formExcluirAvaliacao = document.querySelector('#formExcluirAvaliacao');
const listBtnExcluirAvaliacao = document.querySelectorAll('.btnExcluirAvaliacao');
const nomeAvaliacaoExcluir = document.querySelector('#nomeAvaliacaoExcluir');

listBtnExcluirAvaliacao.forEach(btnExcluirAvaliacao => {
    btnExcluirAvaliacao.addEventListener('click', () => {
        const identificador = btnExcluirAvaliacao.getAttribute('data-identificador')
        const avaliacao_id = btnExcluirAvaliacao.getAttribute('data-id')

        nomeAvaliacaoExcluir.textContent = identificador;
        formExcluirAvaliacao.action = `/disciplinas/${document.querySelector('#disciplina_edit').value}/avaliacoes/${avaliacao_id}/delete/`;
    });
});
