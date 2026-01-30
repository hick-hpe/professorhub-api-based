// abreviaturas em portugues
const abrevList = document.querySelectorAll('.abrev');
const eventosTarefas = document.querySelector('#eventosTarefas');

const NAME_DAYS_WEEK = {
    'Mon': 'Segunda',
    'Tue': 'Terça',
    'Wed': 'Quarta',
    'Thu': 'Quinta',
    'Fri': 'Sexta',
    'Sat': 'Sábado',
    'Sun': 'Domingo',
}

STATUS_TAREFA = {
    'criada': 'bg-info',
    'em_andamento': 'bg-warning',
    'concluida': 'bg-success',
    'pendente': 'bg-danger',
}

STATUS_AULA = {
    'pendente': 'bg-secondary',
    'criado': 'bg-info',
    'nao_planejada': 'bg-warning',
    'planejada': 'bg-primary',
    'material_em_desenvolvimento': 'bg-warning',
    'material_concluido': 'bg-success',
}

// destacar dia atual
const dataAtual = new Date();
const diasCalendario = document.querySelectorAll('.dia-calendario');

diasCalendario.forEach((dia) => {
    if (dia.textContent == dataAtual.getDate()) {
        dia.classList.add('dia-atual');
    }
});

// tarefas
const getTarefasAPI = async () => {
    console.log('MESSS -> ', dataAtual.getMonth());
    const response = await fetch(`/tarefas/mes-atual/${dataAtual.getMonth()}/`);
    const data = await response.json();
    return data.tarefas;
}

// aulas
const getAulasAPI = async () => {
    const response = await fetch(`/planos/all/json/`);
    const data = await response.json();
    return data.planos;
}

// datas importantes
const getDatasImportantesAPI = async () => {
    const response = await fetch(`/datas-importantes/mes-atual/${dataAtual.getMonth()}/`);
    const data = await response.json();
    return data.datas;
}

// teste rota, OK -> ajustar layout auals + tarefas
getAulasAPI()
    .then(data => console.log('aulas-dash: ', data))
    .catch(err => console.error('deu ruim :( ', err));

let tarefasPorDia = {};
let aulasPorDia = {};
let datasImportantesPorDia = {};
let dadosTarefasAPI = [];
let dadosAulasAPI = [];
let dadosDatasImportantesAPI = [];

async function atualizarTarefasEAulas() {
    try {
        // aguarda dados das APIs
        dadosTarefasAPI = await getTarefasAPI();
        dadosAulasAPI = await getAulasAPI();
        dadosDatasImportantesAPI = await getDatasImportantesAPI();

        console.log("tarefas recebidas:", dadosTarefasAPI);
        console.log("aulas recebidas:", dadosAulasAPI);
        console.log("datas importantes recebidas:", dadosDatasImportantesAPI);

        // zerar para evitar duplicações quando recarregar
        tarefasPorDia = {};
        aulasPorDia = {};
        datasImportantesPorDia = {};

        // processar tarefas
        dadosTarefasAPI.forEach(tarefa => {
            const [ano, mes, dia] = tarefa.prazo.split('-');
            const chave = `dia-${Number(dia)}-${Number(mes) - 1}-${Number(ano)}`;

            if (!tarefasPorDia[chave]) tarefasPorDia[chave] = [];
            tarefasPorDia[chave].push(tarefa);
        });

        // processar aulas
        dadosAulasAPI.forEach(aula => {
            const [ano, mes, dia] = aula.data.split('-');
            const chave = `dia-${Number(dia)}-${Number(mes) - 1}-${Number(ano)}`;

            if (!aulasPorDia[chave]) aulasPorDia[chave] = [];
            aulasPorDia[chave].push(aula);
        });

        // processar datas importantes
        dadosDatasImportantesAPI.forEach(dataImportante => {
            const [ano, mes, dia] = dataImportante.data.split('-');
            const chave = `dia-${Number(dia)}-${Number(mes) - 1}-${Number(ano)}`;

            if (!datasImportantesPorDia[chave]) datasImportantesPorDia[chave] = [];
            datasImportantesPorDia[chave].push(dataImportante);
        });

        // preencher o calendário
        const diasComConteudo = new Set([
            ...Object.keys(tarefasPorDia),
            ...Object.keys(aulasPorDia),
            ...Object.keys(datasImportantesPorDia)
        ]);

        diasComConteudo.forEach(chave => {
            const dia = Number(chave.split("-")[1]);
            adicionarConteudoDoDia(dia);
        });

        // eventos de tarefas
        adicionarEventosTarefas(dadosTarefasAPI);

    } catch (err) {
        console.error("Erro ao atualizar tarefas e aulas:", err);
    }
}

// exibir a tarefa no dia especificado
function adicionarConteudoDoDia(dia) {
    console.log("############# ADD CONTEÚDO NO DIA #############");

    const chave = `dia-${dia}-${dataAtual.getMonth()}-${dataAtual.getFullYear()}`;
    const td = document.querySelector(`#${chave}`);

    if (!td) return;

    const tarefas = tarefasPorDia[chave] || [];
    const aulas = aulasPorDia[chave] || [];
    const datasImportantes = datasImportantesPorDia[chave] || [];

    const LIMITE_TAREFAS_POR_DIA = 3;
    const LIMITE_AULAS_POR_DIA = 2;

    const htmlTarefas = tarefas.length > 0
        ? `
        <div class="eventos mt-auto d-flex gap-1 justify-content-center">
            ${tarefas.map(tarefa =>
            `<div class="evento ${STATUS_TAREFA[tarefa.status]}" title="${tarefa.nome}"></div>`
        ).join('')}
        </div>`
        : '';

    const aulasExibir = aulas.slice(0, LIMITE_AULAS_POR_DIA);
    const htmlAulas = aulasExibir.length > 0
        ? `
    <div class="text-center d-flex flex-column gap-1">
        ${aulasExibir.map(aula =>
            `<span class="badge ${STATUS_AULA[aula.status] || 'bg-secondary'} mx-auto" 
                title="${aula.disciplina__nome} | ${aula.titulo} | Status: ${aula.status}" 
                style="font-size: 0.65rem; max-width: 70px; padding: 0.15rem 0.3rem;"
                >
                ${aula.titulo}
            </span>`
        ).join('')}
        ${aulas.length > LIMITE_AULAS_POR_DIA 
            ? `<span class="badge bg-secondary text-truncate mx-auto" style="font-size: 0.6rem; padding: 0.1rem 0.25rem;">+${aulas.length - LIMITE_AULAS_POR_DIA}</span>` 
            : ''}
    </div>`
        : '';

    const htmlDatasImportantes = datasImportantes.length > 0
        ? `
        <div class="eventos d-flex gap-1 justify-content-center">
            ${datasImportantes.map(data =>
                `<div class="evento ${data.dia_letivo ? 'bg-info' : 'bg-danger'}" title="${data.detalhes}"></div>`
            ).join('')}
        </div>`
        : '';

    const conteudo = `
        <div class="d-flex flex-column justify-content-between h-100 p-1" style="font-size: 0.75rem;">
            <div class="fw-bold">${dia}</div>

            ${tarefas.length > LIMITE_TAREFAS_POR_DIA
            ? `<div class="badge text-bg-secondary" style="font-size: 0.6rem;">+${tarefas.length - LIMITE_TAREFAS_POR_DIA}</div>`
            : ''
        }

            ${htmlAulas}
            ${htmlDatasImportantes}
            ${htmlTarefas}
        </div>
    `;

    td.innerHTML = conteudo;
    
    // Marcar dias não letivos com fundo vermelho
    const temDiaNaoLetivo = datasImportantes.some(d => !d.dia_letivo);
    if (temDiaNaoLetivo) {
        td.style.backgroundColor = '#ffe6e6';
    }
};

// aba eventos
function adicionarEventosTarefas(data) {
    console.log('data: ', data)
    eventosTarefas.innerHTML = '';

    if (data.length == 0) {
        eventosTarefas.innerHTML = '<div class="alert alert-info">Nenhum evento encontrado.</div>';
    } else {
        data.forEach(tarefa => {
            console.log(tarefa);
            const data_split = tarefa.prazo.split('-');
            eventosTarefas.innerHTML += `
                <li
                    class="list-group-item mb-3 p-3 shadow-sm border rounded bg-transparent">
                    <div
                        class="d-flex justify-content-between align-items-start mb-2">
                        <a href="/tarefas/"
                            class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-journal-text"></i>
                            Ver tarefa
                        </a>
                        <div>
                            <span class="badge ${STATUS_TAREFA[tarefa.status]} text-${STATUS_TAREFA[tarefa.status]}"> ${tarefa.get_status_display}</span>
                        </div>
                    </div>

                    <div class="d-flex">
                        <div
                            class="text-center me-3 border-end"
                            style="width: 100px;">
                            <div class="fs-3 fw-bold">${data_split[2]}/${data_split[1]}</div>
                            <small class="text-muted abrev">${NAME_DAYS_WEEK[tarefa.diaSemana]}</small>
                        </div>
                        <div>
                            <h6 class="mb-1 fw-semibold">${tarefa.nome}</h6>
                            <small class="text-muted">${tarefa.descricao}</small><br>
                            <small class="text-muted">Disciplina: ${tarefa.disciplina}</small>
                        </div>
                    </div>
                </li>
            `;
        });
    }
}

// marcar o mes atual
const mesSelelct = document.querySelector('#mes-select');
mesSelelct.value = dataAtual.getMonth();

function atualizarMesSelecionadoEAulas(mes) {
    dataAtual.setMonth(mes);
    mesSelelct.value = mes;
    construirCalendario();
}

mesSelelct.addEventListener('change', () => {
    atualizarMesSelecionadoEAulas(Number(mesSelelct.value));
});

const btnHoje = document.querySelector('#btn-hoje');
btnHoje.addEventListener('click', () => {
    atualizarMesSelecionadoEAulas(new Date().getMonth());
});

// dias antes do mes atual
function construirCalendario() {
    // construir calendario
    const numDiasMesPassado = new Date(dataAtual.getFullYear(), dataAtual.getMonth(), 0).getDate(); // 28, 30, 31
    const diaSemanaPrimeiroDiaMesAtual = new Date(dataAtual.getFullYear(), dataAtual.getMonth(), 1).getDay(); // seg, ter, qua...
    const numDiasMesAtual = new Date(dataAtual.getFullYear(), dataAtual.getMonth() + 1, 0).getDate(); // 28, 30, 31

    // imprimir no console as variaveis

    const corpoCalendario = document.querySelector('#corpo-calendario');
    corpoCalendario.innerHTML = '';

    const tr = document.createElement('tr');
    for (let i = 0; i < diaSemanaPrimeiroDiaMesAtual; i++) {
        const td = document.createElement('td');
        td.classList.add('text-muted');
        td.textContent = numDiasMesPassado - diaSemanaPrimeiroDiaMesAtual + 1 + i;
        tr.appendChild(td);
    }
    corpoCalendario.appendChild(tr);

    // completa a primeira semana com os dias do mes atual
    let diaAtual = 1;
    for (let i = diaSemanaPrimeiroDiaMesAtual; i < 7; i++) {
        const td = document.createElement('td');
        td.classList.add('dia-calendario');
        td.id = `dia-${diaAtual}-${dataAtual.getMonth()}-${dataAtual.getFullYear()}`;
        if (diaAtual === dataAtual.getDate() && (new Date().getMonth() === dataAtual.getMonth())) {
            td.classList.add('hoje');
        }
        td.textContent = diaAtual;
        tr.appendChild(td);
        diaAtual++;
    }

    // dias do mes atual
    let refTR;
    while (diaAtual <= numDiasMesAtual) {
        const tr = document.createElement('tr');
        for (let i = 0; i < 7; i++) {
            if (diaAtual > numDiasMesAtual) {
                break;
            }
            const td = document.createElement('td');
            td.classList.add('dia-calendario');
            td.id = `dia-${diaAtual}-${dataAtual.getMonth()}-${dataAtual.getFullYear()}`;
            if (diaAtual === dataAtual.getDate() && (new Date().getMonth() === dataAtual.getMonth())) {
                td.classList.add('hoje');
            }
            td.textContent = diaAtual;
            tr.appendChild(td);
            diaAtual++;
        }
        corpoCalendario.appendChild(tr);
        refTR = tr;
    }

    // dias depois do mes atual
    const diasFaltando = 7 - refTR.children.length;
    for (let i = 1; i <= diasFaltando; i++) {
        const td = document.createElement('td');
        td.classList.add('text-muted');
        td.textContent = i;
        refTR.appendChild(td);
    }

    atualizarTarefasEAulas();

}

construirCalendario();

