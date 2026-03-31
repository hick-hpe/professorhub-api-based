const modalExcluir = document.getElementById('modalExcluir');

modalExcluir.addEventListener('show.bs.modal', (event) => {
    const button = event.relatedTarget;

    const nomeCalendario = button.getAttribute('data-nome');
    const urlExcluir = button.getAttribute('data-url');

    const spanCalendario = modalExcluir.querySelector('#calendario_excluir');
    spanCalendario.textContent = nomeCalendario;
    
    const form = modalExcluir.querySelector('form');
    form.action = urlExcluir;
    
    const url = button.getAttribute('data-url');

    console.log('nomeCalendario:', nomeCalendario);
    console.log('url:', url);
});
