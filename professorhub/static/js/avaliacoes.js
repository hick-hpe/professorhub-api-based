const formConfirmExcluir = document.querySelector('#confirm-excluir');
const formEdit = document.querySelector('#formEdit');
const modal_delete = document.querySelector('#modal_delete');
const modal_edit = document.querySelector('#modal_edit');
const tbodyAvaliacoes = document.querySelector('#tbodyAvaliacoes');
const status_filter = document.querySelector('#status_filter');
const pesquisarAvaliacoes = document.querySelector('#pesquisarAvaliacoes');

modal_delete.addEventListener('show.bs.modal', (e) => {
    const btn_delete = e.relatedTarget;
    const id = btn_delete.getAttribute('data-id');
    formConfirmExcluir.action = `/avaliacoes/${id}/delete/`;
});

status_filter.addEventListener('change', () => {
    let texto = status_filter.options[status_filter.selectedIndex].text;
    console.log(texto);
    if (texto == 'Todas') texto = '';
    for (const tr of tbodyAvaliacoes.children) {
        if (!tr.innerHTML.includes(texto)) {
            tr.style.display = 'none';
        } else {
            tr.style.display = '';
        }
    }
});

const getPlanos = async (disciplinaId) => {
    try {
        const response = await fetch(`/disciplinas/${disciplinaId}/planos/json/`, {
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

modal_edit.addEventListener('show.bs.modal', async (e) => {
    const btn_edit = e.relatedTarget;
    const disciplina = btn_edit.getAttribute('data-disciplina');
    await listarPlanos(disciplina);

    const id = btn_edit.getAttribute('data-id');
    const identificador = btn_edit.getAttribute('data-identificador');
    const plano_aula = btn_edit.getAttribute('data-plano-aula');
    const etapa = btn_edit.getAttribute('data-etapa');
    const tipo = btn_edit.getAttribute('data-tipo');
    const data = btn_edit.getAttribute('data-data');
    const status = btn_edit.getAttribute('data-status');

    // exibir dados no console
    console.log('id:', id);
    console.log('identificador:', identificador);
    console.log('plano_aula:', plano_aula);
    console.log('disciplina:', disciplina);
    console.log('etapa:', etapa);
    console.log('tipo:', tipo);
    console.log('data:', data);
    console.log('status:', status);

    formEdit.action = `/avaliacoes/${id}/editar/`;
    document.querySelector('#identificador_edit').value = identificador;
    document.querySelector('#plano_aula_edit').value = String(plano_aula);
    document.querySelector('#disciplina_edit').value = disciplina;
    document.querySelector('#tipo_edit').value = tipo;
    if (etapa)
        document.querySelector('#etapa_edit').value = etapa;
    else
        document.querySelector('#etapa_edit').placeholder = 'Não definido';
    document.querySelector('#data_edit').value = data;
    document.querySelector('#status_edit').value = status;
});

// filtrar avaliações
pesquisarAvaliacoes.addEventListener('input', (e) => {
    const texto = e.target.value.toLowerCase();

    for (const tr of tbodyAvaliacoes.children) {
        if (!tr.innerHTML.toLowerCase().includes(texto)) {
            tr.style.display = 'none';
        } else {
            tr.style.display = '';
        }
    }
});
