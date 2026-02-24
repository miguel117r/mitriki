let roomId = null;
let playerId = null;
let role = null;
let gameActive = false;

async function createAIGame() {
    const res = await fetch('/api/triki/create_ai_game', { method: 'POST' });
    const data = await res.json();
    initGame(data);
}

async function createRoom() {
    const res = await fetch('/api/triki/create_room', { method: 'POST' });
    const data = await res.json();
    initGame(data);
}

async function joinRoom() {
    const rid = document.getElementById('room-input').value;
    const res = await fetch('/api/triki/join_room', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_id: rid })
    });
    if (res.ok) {
        const data = await res.json();
        initGame(data);
    } else {
        alert("Sala no válida o llena");
    }
}

function initGame(data) {
    roomId = data.room_id;
    playerId = data.player_id;
    role = data.role;
    gameActive = true;
    document.getElementById('setup').style.display = 'none';
    document.getElementById('game-view').style.display = 'block';
    document.getElementById('room-info').innerText = roomId.startsWith('AI') ? "Modo: vs Computadora" : `Sala: ${roomId} | Eres: ${role}`;
    startPolling();
}

async function makeMove(row, col) {
    if (!gameActive) return;
    const res = await fetch(`/api/triki/${roomId}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col, role, player_id: playerId })
    });
    const state = await res.json();
    renderBoard(state);
}

async function restartGame() {
    await fetch(`/api/triki/${roomId}/restart`, { method: 'POST' });
    document.getElementById('restart-btn').style.display = 'none';
}

function renderBoard(state) {
    const boardEl = document.getElementById('board');
    boardEl.innerHTML = "";
    state.board.forEach((row, r) => {
        row.forEach((val, c) => {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.innerText = val;
            cell.onclick = () => { if (val === "" && state.turn === role) makeMove(r, c); };
            boardEl.appendChild(cell);
        });
    });

    const turnInfo = document.getElementById('turn-info');
    if (state.game_over) {
        turnInfo.innerText = state.winner ? `¡GANADOR: ${state.winner}!` : "¡EMPATE!";
        turnInfo.style.color = state.winner === role ? "#00ff88" : "#f85149";
        document.getElementById('restart-btn').style.display = 'block';
    } else {
        turnInfo.innerText = state.turn === role ? "Tu turno" : (state.vs_ai ? "Pensando..." : "Turno rival");
        turnInfo.style.color = state.turn === role ? "#00ff88" : "#8b949e";
    }
    document.getElementById('scores').innerText = `X: ${state.scores.X} - O: ${state.scores.O}`;
}

function startPolling() {
    setInterval(async () => {
        if (!gameActive) return;
        const res = await fetch(`/api/triki/${roomId}/state/${playerId}`);
        if (res.ok) {
            const state = await res.json();
            renderBoard(state);
        }
    }, 1000);
}
