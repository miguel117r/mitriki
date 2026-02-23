// minesweeper.js
const API_BASE = window.location.origin + '/api/minesweeper';
let gameId = null;

document.getElementById('new-game-button').addEventListener('click', startNewGame);

async function startNewGame() {
    const res = await fetch(`${API_BASE}/new_game`, { method: 'POST' });
    const data = await res.json();
    gameId = data.game_id;
    renderBoard(data.initial_state);
    document.getElementById('game-status').textContent = "Juego iniciado. ¡Cuidado con las minas!";
}

function renderBoard(state) {
    const container = document.getElementById('mine-board-container');
    container.innerHTML = '';
    container.style.gridTemplateColumns = `repeat(${state.cols}, 30px)`;

    state.visible.forEach((row, r) => {
        row.forEach((cell, c) => {
            const div = document.createElement('div');
            div.className = `cell ${cell}`;
            
            if (cell === 'revealed') {
                const val = state.values[r][c];
                if (val === 'M') {
                    div.textContent = '💣';
                    div.classList.add('mine');
                } else if (val !== '0') {
                    div.textContent = val;
                    div.classList.add(`n${val}`);
                }
            } else if (cell === 'flagged') {
                div.textContent = '🚩';
            }

            div.onclick = () => revealCell(r, c);
            div.oncontextmenu = (e) => {
                e.preventDefault();
                toggleFlag(r, c);
            };
            container.appendChild(div);
        });
    });

    if (state.game_over) {
        document.getElementById('game-status').textContent = state.winner ? "¡GANASTE! 🎉" : "¡BOOM! Perdiste 💥";
    }
}

async function revealCell(r, c) {
    if (!gameId) return;
    const res = await fetch(`${API_BASE}/${gameId}/reveal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row: r, col: c })
    });
    const state = await res.json();
    renderBoard(state);
}

async function toggleFlag(r, c) {
    if (!gameId) return;
    const res = await fetch(`${API_BASE}/${gameId}/flag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row: r, col: c })
    });
    const state = await res.json();
    renderBoard(state);
}
