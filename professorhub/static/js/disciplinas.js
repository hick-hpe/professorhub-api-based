const checkboxes = document.getElementsByName('dias[]');
const span_carga_horaria = document.getElementById('span_carga_horaria');
const span_dias_aulas = document.getElementById('span_dias_aulas');
const div_aviso = document.getElementById('div_aviso');
const disciplina_excluir = document.getElementById('disciplina_excluir');
const modalExcluir = document.getElementById('modalExcluir');

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        const inputAula = document.querySelector(`#aulas_${checkbox.id}`);
        if (inputAula) {
            inputAula.disabled = !checkbox.checked;
            inputAula.required = checkbox.checked;
        }
    });
});

modalExcluir.addEventListener('show.bs.modal', (event) => {
    const button = event.relatedTarget;

    const nomeDisciplina = button.getAttribute('data-nome');
    const urlExcluir = button.getAttribute('data-url');

    const spanDisciplina = modalExcluir.querySelector('#disciplina_excluir');
    spanDisciplina.textContent = nomeDisciplina;

    const form = modalExcluir.querySelector('form');
    form.action = urlExcluir;
});


