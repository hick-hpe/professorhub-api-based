const formEditarPlano = document.querySelector('#formEditarPlano');
const modalEditarPlano = document.querySelector('#modalEditarPlano');
const listBtnEditarPlano = document.querySelectorAll('.btnEditarPlano');

listBtnEditarPlano.forEach(btnEditarPlano => {
    btnEditarPlano.addEventListener('click', () => {
        const disciplina_id = btnEditarPlano.getAttribute('data-disciplina-id')
        const plano_id = btnEditarPlano.getAttribute('data-id')
        formEditarPlano.action = `/disciplinas/${disciplina_id}/planos/${plano_id}/editar`;
        
        const titulo = btnEditarPlano.getAttribute('data-titulo');
        const objetivo = btnEditarPlano.getAttribute('data-objetivo');
        const conteudos = btnEditarPlano.getAttribute('data-conteudo');
        const status = btnEditarPlano.getAttribute('data-status');
        const data = btnEditarPlano.getAttribute('data-data');

        document.querySelector('#titulo_edit').value = titulo;
        document.querySelector('#objetivos_edit').textContent = objetivo;
        document.querySelector('#conteudos_edit').textContent = conteudos;
        document.querySelector('#status_edit').value = status;
        document.querySelector('#data_edit').value = data;
    });
});


const formExcluirPlano = document.querySelector('#formExcluirPlano');
const listBtnExcluirPlano = document.querySelectorAll('.btnExcluirPlano');
const nomePlanoExcluir = document.querySelector('#nomePlanoExcluir');

listBtnExcluirPlano.forEach(btnExcluirPlano => {
    btnExcluirPlano.addEventListener('click', () => {
        const titulo = btnExcluirPlano.getAttribute('data-titulo')
        const disciplina_id = btnExcluirPlano.getAttribute('data-disciplina-id')
        const plano_id = btnExcluirPlano.getAttribute('data-id')

        nomePlanoExcluir.textContent = titulo;
        formExcluirPlano.action = `/disciplinas/${disciplina_id}/planos/${plano_id}/excluir`;
    });
});

