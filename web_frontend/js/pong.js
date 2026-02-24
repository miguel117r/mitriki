// pong.js
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('game-status');

const WINNING_SCORE = 10;
let gameRunning = false;
let mode = 'ia'; 

// Ajuste de velocidad: Inicial más lenta (3 en lugar de 4)
const ball = { x: 400, y: 200, dx: 3, dy: 3, radius: 10, speedLimit: 7 };
const paddleWidth = 12, paddleHeight = 90; // Paletas un poco más grandes para mejor control
const player1 = { x: 0, y: 155, score: 0 };
const player2 = { x: canvas.width - paddleWidth, y: 155, score: 0 };

const keys = {};
window.addEventListener('keydown', e => keys[e.code] = true);
window.addEventListener('keyup', e => keys[e.code] = false);

// --- CONTROLES TÁCTILES ---
canvas.addEventListener('touchstart', handleTouch, {passive: false});
canvas.addEventListener('touchmove', handleTouch, {passive: false});
canvas.addEventListener('touchend', () => {
    keys['TouchP1Up'] = false; keys['TouchP1Down'] = false;
    keys['TouchP2Up'] = false; keys['TouchP2Down'] = false;
}, {passive: false});

function handleTouch(e) {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const scaleY = canvas.height / rect.height;
    const touch = e.touches[0];
    const touchY = (touch.clientY - rect.top) * scaleY;

    if (touchY < player1.y + paddleHeight / 2) {
        keys['TouchP1Up'] = true; keys['TouchP1Down'] = false;
    } else {
        keys['TouchP1Up'] = false; keys['TouchP1Down'] = true;
    }
}

document.getElementById('btn-ia').onclick = () => start('ia');
document.getElementById('btn-pvp').onclick = () => start('pvp');

function start(m) {
    mode = m;
    gameRunning = true;
    player1.score = player2.score = 0;
    player1.y = player2.y = (canvas.height - paddleHeight) / 2;
    resetBall();
    status.textContent = mode === 'ia' ? "vs Computadora" : "vs Jugador 2";
    status.style.color = "#00ff88";
    requestAnimationFrame(update);
}

function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    // Velocidad inicial controlada
    const startSpeed = 3.5;
    ball.dx = (Math.random() > 0.5 ? startSpeed : -startSpeed);
    ball.dy = (Math.random() > 0.5 ? startSpeed - 0.5 : -(startSpeed - 0.5));
}

function checkWinner() {
    if (player1.score >= WINNING_SCORE) {
        gameRunning = false;
        status.textContent = "¡JUGADOR 1 GANA! 🏆";
        status.style.color = "#00ff88";
    } else if (player2.score >= WINNING_SCORE) {
        gameRunning = false;
        status.textContent = mode === 'ia' ? "¡LA IA GANA! 🤖" : "¡JUGADOR 2 GANA! 🏆";
        status.style.color = "#f44336";
    }
}

function update() {
    if (!gameRunning) return;

    // Movimiento paletas: Velocidad ajustada a 7 para mejor reacción
    const paddleSpeed = 7;
    if ((keys['KeyW'] || keys['TouchP1Up']) && player1.y > 0) player1.y -= paddleSpeed;
    if ((keys['KeyS'] || keys['TouchP1Down']) && player1.y < canvas.height - paddleHeight) player1.y += paddleSpeed;

    if (mode === 'pvp') {
        if (keys['ArrowUp'] && player2.y > 0) player2.y -= paddleSpeed;
        if (keys['ArrowDown'] && player2.y < canvas.height - paddleHeight) player2.y += paddleSpeed;
    } else {
        // IA más equilibrada: No es perfecta
        const target = ball.y - paddleHeight / 2;
        const aiSpeed = 4.5; // Un poco más lenta que el jugador
        if (player2.y < target - 10) player2.y += aiSpeed;
        if (player2.y > target + 10) player2.y -= aiSpeed;
    }

    ball.x += ball.dx;
    ball.y += ball.dy;

    // Rebote superior/inferior
    if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) ball.dy *= -1;

    // Rebote paletas con limitador de velocidad (Max speedLimit)
    const accel = 1.04; // Aceleración más suave
    if (ball.x - ball.radius < player1.x + paddleWidth && ball.y > player1.y && ball.y < player1.y + paddleHeight) {
        ball.dx = Math.min(Math.abs(ball.dx * accel), ball.speedLimit);
        ball.x = player1.x + paddleWidth + ball.radius;
    }
    if (ball.x + ball.radius > player2.x && ball.y > player2.y && ball.y < player2.y + paddleHeight) {
        ball.dx = -Math.min(Math.abs(ball.dx * accel), ball.speedLimit);
        ball.x = player2.x - ball.radius;
    }

    if (ball.x < 0) { player2.score++; resetBall(); checkWinner(); }
    if (ball.x > canvas.width) { player1.score++; resetBall(); checkWinner(); }

    draw();
    if (gameRunning) requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Red de en medio
    ctx.setLineDash([10, 10]);
    ctx.strokeStyle = 'rgba(0, 255, 136, 0.2)';
    ctx.beginPath();
    ctx.moveTo(canvas.width/2, 0); ctx.lineTo(canvas.width/2, canvas.height);
    ctx.stroke();
    ctx.setLineDash([]);

    // Paletas con estilo Neón
    ctx.fillStyle = '#00ff88';
    ctx.shadowBlur = 10; ctx.shadowColor = '#00ff88';
    ctx.fillRect(player1.x, player1.y, paddleWidth, paddleHeight);
    ctx.fillStyle = '#00d4ff';
    ctx.shadowColor = '#00d4ff';
    ctx.fillRect(player2.x, player2.y, paddleWidth, paddleHeight);

    // Bola blanca brillante
    ctx.fillStyle = '#fff';
    ctx.shadowBlur = 15; ctx.shadowColor = '#fff';
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Marcadores
    ctx.font = 'bold 30px Orbitron';
    ctx.fillStyle = '#00ff88';
    ctx.fillText(player1.score, 200, 50);
    ctx.fillStyle = '#00d4ff';
    ctx.fillText(player2.score, 560, 50);
}
