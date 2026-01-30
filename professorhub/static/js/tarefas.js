const formConfirmExcluir = document.querySelector('#confirm-excluir');
const formEdit = document.querySelector('#formEdit');
const modal_delete = document.querySelector('#modal_delete');
const modal_edit = document.querySelector('#modal_edit');
const tbodyTarefas = document.querySelector('#tbodyTarefas');
const status_filter = document.querySelector('#status_filter');
const pesquisarTarefas = document.querySelector('#pesquisarTarefas');

modal_delete.addEventListener('show.bs.modal', (e) => {
    const btn_delete = e.relatedTarget;
    const id = btn_delete.getAttribute('data-id');
    formConfirmExcluir.action = `/tarefas/${id}/delete/`;
});

status_filter.addEventListener('change', () => {
    let option = status_filter.options[status_filter.selectedIndex];
    let texto = option.text;
    let value = option.value;

    if (value == '') texto = '';
    for (const tr of tbodyTarefas.children) {
        if (!tr.innerHTML.includes(texto)) {
            tr.style.display = 'none';
        } else {
            tr.style.display = '';
        }
    }
});

const getPlanos = async (disciplinaId) => {
    try {
        const response = await fetch(`/disciplinas/${disciplinaId}/planos/`, {
            method: "GET",
            credentials: "include"
        });
        if (!response.ok) {
            throw new Error('Erro ao buscar planos de aula');
        }
        const data = await response.json();
        return data.planos;
    } catch (error) {
        console.error('Erro na requisição:', error);
        return [];
    }
};

const listarPlanos = async (disciplinaId) => {
    const planos_aulas = await getPlanos(disciplinaId);

    // exibir planos de aula no select
    const selectPlanoAula = document.querySelector('#plano_aula_edit');
    selectPlanoAula.innerHTML = '<option value selected disabled>Selecione o plano de aula</option>';
    planos_aulas.forEach(plano => {
        const option = document.createElement('option');
        option.value = plano.id;
        option.textContent = plano.titulo;
        selectPlanoAula.appendChild(option);
    });
};

document.querySelector('#disciplina_edit').addEventListener('change', async (e) => {
    const disciplinaId = e.target.value;
    listarPlanos(disciplinaId);
});

modal_edit.addEventListener('show.bs.modal', (e) => {
    const btn_edit = e.relatedTarget;
    const id = btn_edit.getAttribute('data-id');
    const nome = btn_edit.getAttribute('data-nome');
    const descricao = btn_edit.getAttribute('data-descricao');
    const disciplina = btn_edit.getAttribute('data-disciplina');
    const plano_aula = btn_edit.getAttribute('data-plano-aula');
    const prazo = btn_edit.getAttribute('data-prazo');
    const status = btn_edit.getAttribute('data-status');

    formEdit.action = `/tarefas/${id}/`;
    document.querySelector('#nome_edit').value = nome;
    document.querySelector('#descricao_edit').value = descricao;
    document.querySelector('#disciplina_edit').value = disciplina;
    document.querySelector('#plano_aula_edit').value = plano_aula;
    document.querySelector('#prazo_edit').value = prazo;
    document.querySelector('#status_edit').value = status;
});

// filtrar tarefas
pesquisarTarefas.addEventListener('input', (e) => {
    const texto = e.target.value.toLowerCase();

    for (const tr of tbodyTarefas.children) {
        if (!tr.innerHTML.toLowerCase().includes(texto)) {
            tr.style.display = 'none';
        } else {
            tr.style.display = '';
        }
    }
});