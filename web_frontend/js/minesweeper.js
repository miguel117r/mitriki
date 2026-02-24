let gameId = null;
const grid = document.getElementById("minesweeper-grid");
const status = document.getElementById("status");

const difficulties = {
    facil: { rows: 8, cols: 8, mines: 10 },
    normal: { rows: 12, cols: 12, mines: 25 },
    dificil: { rows: 16, cols: 16, mines: 50 },
    imposible: { rows: 20, cols: 20, mines: 100 }
};

async function startGame(level = 'facil') {
    // Actualizar botones UI
    document.querySelectorAll('.diff-btn').forEach(btn => {
        btn.classList.toggle('active', btn.innerText.toLowerCase() === level);
    });

    const config = difficulties[level];
    status.innerText = "Iniciando...";
    status.style.color = "inherit";

    const res = await fetch('/api/minesweeper/new_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    });
    const data = await res.json();
    gameId = data.game_id;
    renderGrid(data.initial_state);
}

function renderGrid(state) {
    grid.innerHTML = "";
    grid.style.gridTemplateColumns = `repeat(${state.cols}, 30px)`;
    
    for (let r = 0; r < state.rows; r++) {
        for (let c = 0; c < state.cols; c++) {
            const cell = document.createElement("div");
            cell.className = "cell";
            const val = state.values[r][c];
            const vis = state.visible[r][c];

            if (vis === "revealed") {
                cell.classList.add("revealed");
                if (val === "M") {
                    cell.innerText = "💣";
                    cell.classList.add("mine");
                } else {
                    cell.innerText = val === "0" ? "" : val;
                    cell.setAttribute("data-value", val);
                }
            } else if (vis === "flagged") {
                cell.classList.add("flagged");
                cell.innerText = "🚩";
            }

            cell.onclick = () => revealCell(r, c);
            cell.oncontextmenu = (e) => {
                e.preventDefault();
                toggleFlag(r, c);
            };
            grid.appendChild(cell);
        }
    }

    if (state.game_over) {
        if (state.winner) {
            status.innerText = "¡FELICIDADES! HAS GANADO";
            status.style.color = "#3fb950";
        } else {
            status.innerText = "¡BOOM! JUEGO TERMINADO";
            status.style.color = "#f85149";
        }
    } else {
        status.innerText = "";
    }
}

async function revealCell(row, col) {
    if (!gameId) return;
    const res = await fetch(`/api/minesweeper/${gameId}/reveal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col })
    });
    const state = await res.json();
    renderGrid(state);
}

async function toggleFlag(row, col) {
    if (!gameId) return;
    const res = await fetch(`/api/minesweeper/${gameId}/flag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col })
    });
    const state = await res.json();
    renderGrid(state);
}

// Iniciar primer juego
startGame('facil');
