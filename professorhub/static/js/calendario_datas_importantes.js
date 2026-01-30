document.addEventListener('DOMContentLoaded', () => {
    // editar
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

    // delete
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
});