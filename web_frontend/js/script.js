// script.js - Lógica del Frontend de Triki
const API_BASE_URL = window.location.origin + '/api/triki';
let gameId = null;
let currentPlayer = 'X';
let boardElement = null;
let currentMode = 'pvp';

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('triki-board-container')) {
        boardElement = document.getElementById('triki-board-container');
        document.getElementById('new-game-button').addEventListener('click', () => startNewGame(currentMode));
        document.getElementById('btn-ia').addEventListener('click', () => startNewGame('ia'));
        document.getElementById('btn-pvp').addEventListener('click', () => startNewGame('pvp'));
        updateStatus('Elige un modo para empezar.');
    }
});

function updateStatus(message, isError = false) {
    const statusElement = document.getElementById('game-status');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.style.color = isError ? 'red' : 'black';
    }
}

async function startNewGame(mode) {
    currentMode = mode;
    updateStatus(`Iniciando nueva partida ${mode === 'ia' ? 'contra IA' : 'PvP'}...`);
    try {
        const response = await fetch(`${API_BASE_URL}/new_game`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        const data = await response.json();
        if (response.ok) {
            gameId = data.game_id;
            currentPlayer = 'X';
            renderBoard(data.initial_state.board);
            updateStatus(`Partida iniciada (${mode}). Turno de ${data.initial_state.current_player}.`);
        } else {
            updateStatus(`Error: ${data.message}`, true);
        }
    } catch (error) {
        updateStatus(`Error de conexión: ${error.message}`, true);
    }
}

async function makeMove(row, col) {
    if (!gameId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/${gameId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ row, col, player: currentPlayer })
        });
        const data = await response.json();

        if (response.ok) {
            const state = data.new_state;
            renderBoard(state.board);
            if (state.game_over) {
                updateStatus(state.winner ? `¡Ganador: ${state.winner}!` : '¡Empate!');
                gameId = null;
            } else {
                currentPlayer = state.current_player;
                updateStatus(`Turno de ${currentPlayer}.`);
            }
        } else {
            updateStatus(data.message, true);
        }
    } catch (error) {
        updateStatus(`Error: ${error.message}`, true);
    }
}

function renderBoard(board) {
    boardElement.innerHTML = '';
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
    boardElement.appendChild(table);
}
