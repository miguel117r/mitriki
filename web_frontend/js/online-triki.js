// online-triki.js
const API_BASE = window.location.origin + '/api/triki';
let roomId = null;
let playerId = null;
let role = null;
let isMyTurn = false;
let pollingInterval = null;

document.getElementById('btn-create').onclick = createRoom;
document.getElementById('btn-join').onclick = joinRoom;

async function createRoom() {
    const res = await fetch(`${API_BASE}/create_room`, { method: 'POST' });
    const data = await res.json();
    setupGame(data);
}

async function joinRoom() {
    const input = document.getElementById('input-room').value;
    if (!input) return alert("Introduce un código");
    const res = await fetch(`${API_BASE}/join_room`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_id: input })
    });
    if (res.ok) {
        setupGame(await res.json());
    } else {
        alert("Sala no encontrada o llena");
    }
}

function setupGame(data) {
    roomId = data.room_id;
    playerId = data.player_id;
    role = data.role;
    document.getElementById('room-display').textContent = `SALA: ${roomId}`;
    document.getElementById('role-display').textContent = `ERES: ${role}`;
    startPolling();
}

async function startPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(fetchState, 1500);
}

async function fetchState() {
    if (!roomId || !playerId) return;
    const res = await fetch(`${API_BASE}/${roomId}/state/${playerId}`);
    const state = await res.json();
    renderBoard(state.board);
    
    isMyTurn = state.turn === role && state.players_count === 2;
    
    if (state.players_count < 2) {
        updateStatus("Esperando oponente...");
    } else if (state.game_over) {
        updateStatus(state.winner ? `¡GANADOR: ${state.winner}! 🎉` : "¡EMPATE! 🤝");
        clearInterval(pollingInterval);
    } else {
        updateStatus(isMyTurn ? "TU TURNO ⚡" : "Esperando movimiento...");
    }
}

function updateStatus(msg) {
    document.getElementById('game-status').textContent = msg;
}

async function makeMove(r, c) {
    if (!isMyTurn || !roomId) return;
    const res = await fetch(`${API_BASE}/${roomId}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_id: roomId, player_id: playerId, role: role, row: r, col: c })
    });
    const state = await res.json();
    renderBoard(state.board);
}

function renderBoard(board) {
    const container = document.getElementById('triki-board-container');
    container.innerHTML = '';
    const table = document.createElement('table');
    table.className = 'triki-board';
    board.forEach((row, r) => {
        const tr = document.createElement('tr');
        row.forEach((cell, c) => {
            const td = document.createElement('td');
            td.textContent = cell;
            if (cell === 'X') td.classList.add('player-x');
            if (cell === 'O') td.classList.add('player-o');
            td.onclick = () => makeMove(r, c);
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
    container.appendChild(table);
}
