document.addEventListener('DOMContentLoaded', () => {
    // editar datas
    const modalEdit = document.getElementById('modal_edit');
    modalEdit.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const calendarioId = button.getAttribute('data-id-calendario');
        const data = button.getAttribute('data-data');
        const detalhes = button.getAttribute('data-detalhes');
        const diaLetivo = button.getAttribute('data-dia-letivo') === 'True';

        modalEdit.querySelector('#edit_data').value = data;
        modalEdit.querySelector('#edit_detalhes').value = detalhes;
        modalEdit.querySelector('#edit_dia_letivo').checked = diaLetivo;

        const formEdit = modalEdit.querySelector('#form_edit');
        formEdit.action = `/calendarios/${calendarioId}/datas-importantes/${id}/`;
    });

    // delete datas
    const modalDelete = document.getElementById('modal_delete');
    modalDelete.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const calendarioId = button.getAttribute('data-id-calendario');
        const dataText = button.getAttribute('data-data');

        const dataModalDelete = modalDelete.querySelector('#data_modal_delete');
        dataModalDelete.textContent = dataText;

        const formDelete = modalDelete.querySelector('#form_delete');
        formDelete.action = `/calendarios/${calendarioId}/datas-importantes/${id}/delete/`;
    });

    // editar períodos
    const modalEditPeriodo = document.getElementById('modal_edit_periodo');
    modalEditPeriodo.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const calendarioId = button.getAttribute('data-id-calendario');
        const dataInicio = button.getAttribute('data-data-inicio');
        const dataFim = button.getAttribute('data-data-fim');
        const detalhes = button.getAttribute('data-detalhes');
        const diaLetivo = button.getAttribute('data-eh-letivo') === 'True';

        console.log('dados recebidos para edição do período:');
        console.log(dataInicio);
        console.log(dataFim);
        console.log(detalhes);
        console.log(diaLetivo);

        modalEditPeriodo.querySelector('#edit_data_inicio_periodo').value = dataInicio;
        modalEditPeriodo.querySelector('#edit_data_fim_periodo').value = dataFim;
        modalEditPeriodo.querySelector('#edit_detalhes_periodo').value = detalhes;
        modalEditPeriodo.querySelector('#edit_eh_letivo_periodo').checked = diaLetivo;

        const formEditPeriodo = modalEditPeriodo.querySelector('#form_edit_periodo');
        formEditPeriodo.action = `/calendarios/${calendarioId}/periodos-importantes/${id}/`;
    });
    
    // delete períodos
    const modalDeletePeriodo = document.getElementById('modal_delete_periodo');
    modalDeletePeriodo.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const calendarioId = button.getAttribute('data-id-calendario');
        const dataText = button.getAttribute('data-detalhes');

        const dataModalDelete = modalDeletePeriodo.querySelector('#detalhes_modal_delete_periodo');
        dataModalDelete.textContent = dataText;

        const formDeletePeriodo = modalDeletePeriodo.querySelector('#form_delete_periodo');
        formDeletePeriodo.action = `/calendarios/${calendarioId}/periodos-importantes/${id}/delete/`;
    });
});