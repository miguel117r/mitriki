// script.js - Lógica del Frontend de Triki
const API_BASE_URL = window.location.origin + '/api/triki'; // URL base dinámica
let gameId = null; // ID de la partida actual
let currentPlayer = 'X'; // El jugador actual en el frontend (para enviar al backend)
let boardElement = null; // Referencia al contenedor del tablero

document.addEventListener('DOMContentLoaded', () => {
    console.log('Frontend web de Multi-Juego cargado correctamente.');

    // Inicializar elementos del DOM solo si estamos en la página de Triki
    if (document.getElementById('triki-board-container')) {
        boardElement = document.getElementById('triki-board-container');
        document.getElementById('new-game-button').addEventListener('click', startNewGame);
        updateStatus('Haz clic en "Nueva Partida" para empezar.');
    }
});

function updateStatus(message, isError = false) {
    const statusElement = document.getElementById('game-status');
    statusElement.textContent = message;
    statusElement.style.color = isError ? 'red' : 'black';
}

async function startNewGame() {
    updateStatus('Iniciando nueva partida...');
    try {
        const response = await fetch(`${API_BASE_URL}/new_game`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (response.ok) {
            gameId = data.game_id;
            currentPlayer = 'X'; // Siempre empezamos como 'X' en el frontend
            renderBoard(data.initial_state.board);
            updateStatus(`Partida #${gameId} iniciada. Turno de ${data.initial_state.current_player}.`);
            // Iniciar el polling para mantener el estado del juego actualizado
            pollGameState();
        } else {
            updateStatus(`Error al iniciar el juego: ${data.message}`, true);
        }
    } catch (error) {
        updateStatus(`Error de conexión: ${error.message}`, true);
        console.error('Error al iniciar nueva partida:', error);
    }
}

async function fetchGameState() {
    if (!gameId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/${gameId}/state`);
        const state = await response.json();

        if (response.ok) {
            renderBoard(state.board);
            if (state.game_over) {
                if (state.winner) {
                    updateStatus(`¡Jugador ${state.winner} ha ganado!`);
                } else {
                    updateStatus('¡Es un empate!');
                }
                gameId = null; // Terminar la partida
            } else {
                updateStatus(`Turno de ${state.current_player}.`);
            }
        } else {
            updateStatus(`Error al obtener estado: ${state.message}`, true);
            gameId = null; // Asumir que la partida ya no existe
        }
        return state; // Devuelve el estado para el polling
    } catch (error) {
        updateStatus(`Error de conexión al obtener estado: ${error.message}`, true);
        console.error('Error al obtener estado de la partida:', error);
        gameId = null; // Asumir que la conexión se perdió
    }
    return null;
}

async function makeMove(row, col) {
    if (!gameId) {
        updateStatus('Por favor, inicia una nueva partida.', true);
        return;
    }

    // Temporalmente asumimos que el jugador actual es 'X'
    // Para multijugador real, necesitaríamos un sistema de autenticación y asignación de jugadores
    const playerToMove = currentPlayer; // Usar el jugador actual del frontend

    updateStatus(`Realizando movimiento para ${playerToMove}...`);
    try {
        const response = await fetch(`${API_BASE_URL}/${gameId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ row, col, player: playerToMove })
        });
        const data = await response.json();

        if (response.ok) {
            renderBoard(data.new_state.board);
            if (data.new_state.game_over) {
                if (data.new_state.winner) {
                    updateStatus(`¡Jugador ${data.new_state.winner} ha ganado!`);
                } else {
                    updateStatus('¡Es un empate!');
                }
                gameId = null;
            } else {
                updateStatus(`Turno de ${data.new_state.current_player}.`);
                // Si el movimiento fue exitoso, alternar el jugador actual para el siguiente movimiento del frontend.
                // Esto es una simplificación para un solo cliente. Para multijugador, el backend dictaría el turno.
                currentPlayer = data.new_state.current_player;
            }
        } else {
            updateStatus(`Error al realizar movimiento: ${data.message}`, true);
            // Si el movimiento falla, obtenemos el estado actual del juego
            fetchGameState();
        }
    } catch (error) {
        updateStatus(`Error de conexión al realizar movimiento: ${error.message}`, true);
        console.error('Error al realizar movimiento:', error);
    }
}

function renderBoard(board) {
    boardElement.innerHTML = ''; // Limpiar tablero existente
    const table = document.createElement('table');
    table.className = 'triki-board';

    board.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        row.forEach((cell, colIndex) => {
            const td = document.createElement('td');
            td.textContent = cell;
            td.dataset.row = rowIndex;
            td.dataset.col = colIndex;
            td.addEventListener('click', () => makeMove(rowIndex, colIndex));
            // Añadir clase para estilo de celda vacía/ocupada
            if (cell === 'X') {
                td.classList.add('player-x');
            } else if (cell === 'O') {
                td.classList.add('player-o');
            }
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
    boardElement.appendChild(table);
}

// Función para polling del estado del juego
async function pollGameState() {
    if (!gameId) return; // Detener polling si no hay partida activa

    const state = await fetchGameState();
    if (state && !state.game_over) {
        // Poll cada 2 segundos
        setTimeout(pollGameState, 2000); 
    }
}