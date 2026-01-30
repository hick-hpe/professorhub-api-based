// modalConfirmarMudancas 
const modalConfirmarMudancas = new bootstrap.Modal(document.querySelector('#confirmarMudarPlano'))

// checkboxes
const checkboxes = document.getElementsByName('dias[]');
checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        console.log(checkbox.id, checkbox.checked);
        const inputAula = document.querySelector(`#aulas_${checkbox.id}`);
        if (inputAula) {
            inputAula.disabled = !checkbox.checked;
        }
    });
});

// dados iniciais que podem iinfluenciar na mudança do plano
const formEdit = document.querySelector('#form-edit');
const cargaHoraria = formEdit.querySelector('#carga_horaria');
let cargaHorariaValue = cargaHoraria.value;

// capturar valores iniciais (direto do atributo data-*)
const dataDias = formEdit.querySelectorAll('input[name="dias[]"]');
const dataAulas = formEdit.querySelectorAll('input[name^="aulas_"]');

const dataDiasIniciais = [];
const dataAulasIniciais = [];

dataDias.forEach(d => dataDiasIniciais.push(d.hasAttribute('checked')));  
dataAulas.forEach(d => dataAulasIniciais.push(d.dataset.aula)); 

console.log('Dados iniciais:');
console.log('Dias:', dataDiasIniciais);
console.log('Aulas:', dataAulasIniciais);
console.log('Carga Horária:', cargaHorariaValue);

// requisição
formEdit.addEventListener('submit', (e) => {
    e.preventDefault();

    // valores atuais do form
    const dataDiasForm = [];
    const dataAulasForm = [];

    dataDias.forEach(d => dataDiasForm.push(d.checked));
    dataAulas.forEach(d => dataAulasForm.push(d.value));

    const cargaHorariaValueForm = cargaHoraria.value;

    // debug
    console.log('Dias (inicial):', dataDiasIniciais);
    console.log('Dias (form):', dataDiasForm);
    console.log('Aulas (inicial):', dataAulasIniciais);
    console.log('Aulas (form):', dataAulasForm);
    console.log('Carga Horária (inicial):', cargaHorariaValue);
    console.log('Carga Horária (form):', cargaHorariaValueForm);

    // determinar se mudou
    const podeMudar =
        podeMudarPlanoDeAula(
            dataDiasIniciais, dataDiasForm,
            dataAulasIniciais, dataAulasForm,
            cargaHorariaValue, cargaHorariaValueForm
        );

    if (podeMudar) {
        modalConfirmarMudancas.show();
    } else {
        salvarNoBanco();
    }
});


function podeMudarPlanoDeAula(dias1, dias2, aulas1, aulas2, carga1, carga2) {
    const listaSaoIguais = (a, b) => a.length === b.length && a.every((val, i) => val === b[i]);

    return (
        !listaSaoIguais(dias1, dias2) ||
        !listaSaoIguais(aulas1, aulas2) ||
        carga1 !== carga2
    )
}

async function salvarNoBanco() {
    const form = document.querySelector('#form-edit');
    const disc_id = document.querySelector('#disciplina_id').value;
    const data = new FormData(form);

    try {
        const response = await fetch(`/disciplinas/${disc_id}/configuracoes/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': data.get('csrfmiddlewaretoken')
            },
            body: data
        });

        if (response.ok) {
            location.reload();
        } else {
            const errText = await response.text();
            console.error('Erro na resposta:', response.status, errText);
        }
    } catch (err) {
        console.log('Erro de rede:', err);
    }
}