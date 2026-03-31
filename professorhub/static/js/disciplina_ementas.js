const modalExcluir = document.getElementById('modalExcluir');
const modalEditar = document.getElementById('modalEditar');

modalEditar.addEventListener('show.bs.modal', (event) => {
    const button = event.relatedTarget;

    const descricao = button.getAttribute('data-descricao');
    const urlEditar = button.getAttribute('data-url');

    const textareaDescricao = modalEditar.querySelector('#ementa_descricao');
    textareaDescricao.value = descricao;

    const form = modalEditar.querySelector('form');
    form.action = urlEditar;
});

modalExcluir.addEventListener('show.bs.modal', (event) => {
    const button = event.relatedTarget;

    const descricao = button.getAttribute('data-descricao');
    const urlExcluir = button.getAttribute('data-url');

    const textareaDescricao = modalExcluir.querySelector('#ementa_excluir');
    textareaDescricao.textContent = descricao;

    const form = modalExcluir.querySelector('form');
    form.action = urlExcluir;
});


