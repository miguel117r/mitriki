// pong.js
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('game-status');

// Configuración inicial
let gameRunning = false;
let mode = 'ia'; // 'ia' o 'pvp'
const ball = { x: 400, y: 200, dx: 4, dy: 4, radius: 10 };
const paddleWidth = 10, paddleHeight = 80;
const player1 = { x: 0, y: 160, score: 0 };
const player2 = { x: canvas.width - paddleWidth, y: 160, score: 0 };

// Teclas
const keys = {};
window.addEventListener('keydown', e => keys[e.code] = true);
window.addEventListener('keyup', e => keys[e.code] = false);

// Botones de modo
document.getElementById('btn-ia').onclick = () => start('ia');
document.getElementById('btn-pvp').onclick = () => start('pvp');

function start(m) {
    mode = m;
    gameRunning = true;
    player1.score = player2.score = 0;
    resetBall();
    status.textContent = mode === 'ia' ? "Jugando contra IA" : "Modo PvP (Local)";
    requestAnimationFrame(update);
}

const WINNING_SCORE = 10;

function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.dx = (Math.random() > 0.5 ? 4 : -4);
    ball.dy = (Math.random() > 0.5 ? 3 : -3);
}

function checkWinner() {
    if (player1.score >= WINNING_SCORE) {
        gameRunning = false;
        status.textContent = "¡JUGADOR 1 GANA LA PARTIDA! 🎉";
        status.style.color = "#4caf50";
    } else if (player2.score >= WINNING_SCORE) {
        gameRunning = false;
        status.textContent = mode === 'ia' ? "¡LA IA GANA LA PARTIDA! 🤖" : "¡JUGADOR 2 GANA LA PARTIDA! 🎉";
        status.style.color = "#f44336";
    }
}

function update() {
    if (!gameRunning) return;

    // ... (movimientos de paletas iguales)
    // Movimiento Jugador 1 (W/S)
    if (keys['KeyW'] && player1.y > 0) player1.y -= 5;
    if (keys['KeyS'] && player1.y < canvas.height - paddleHeight) player1.y += 5;

    // Movimiento Jugador 2 (Flechas o IA)
    if (mode === 'pvp') {
        if (keys['ArrowUp'] && player2.y > 0) player2.y -= 5;
        if (keys['ArrowDown'] && player2.y < canvas.height - paddleHeight) player2.y += 5;
    } else {
        const target = ball.y - paddleHeight / 2;
        if (player2.y < target) player2.y += 3.5;
        if (player2.y > target) player2.y -= 3.5;
    }

    // Movimiento Pelota
    ball.x += ball.dx;
    ball.y += ball.dy;

    // Rebotes y Goles
    if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) ball.dy *= -1;

    if (ball.x - ball.radius < player1.x + paddleWidth && ball.y > player1.y && ball.y < player1.y + paddleHeight) {
        ball.dx *= -1.1;
        ball.x = player1.x + paddleWidth + ball.radius;
    }
    if (ball.x + ball.radius > player2.x && ball.y > player2.y && ball.y < player2.y + paddleHeight) {
        ball.dx *= -1.1;
        ball.x = player2.x - ball.radius;
    }

    if (ball.x < 0) { 
        player2.score++; 
        resetBall(); 
        checkWinner();
    }
    if (ball.x > canvas.width) { 
        player1.score++; 
        resetBall(); 
        checkWinner();
    }

    draw();
    if (gameRunning) requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Línea central
    ctx.setLineDash([10, 10]);
    ctx.strokeStyle = '#fff';
    ctx.beginPath();
    ctx.moveTo(canvas.width/2, 0); ctx.lineTo(canvas.width/2, canvas.height);
    ctx.stroke();

    // Paletas
    ctx.fillStyle = '#fff';
    ctx.fillRect(player1.x, player1.y, paddleWidth, paddleHeight);
    ctx.fillRect(player2.x, player2.y, paddleWidth, paddleHeight);

    // Pelota
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fill();

    // Puntuación
    ctx.font = '30px Courier New';
    ctx.fillText(player1.score, 200, 50);
    ctx.fillText(player2.score, 600, 50);
}
