// pong.js
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('game-status');

const WINNING_SCORE = 10;
let gameRunning = false;
let mode = 'ia'; 

const ball = { x: 400, y: 200, dx: 4, dy: 4, radius: 10 };
const paddleWidth = 10, paddleHeight = 80;
const player1 = { x: 0, y: 160, score: 0 };
const player2 = { x: canvas.width - paddleWidth, y: 160, score: 0 };

const keys = {};
window.addEventListener('keydown', e => keys[e.code] = true);
window.addEventListener('keyup', e => keys[e.code] = false);

// --- CONTROLES TÁCTILES ---
canvas.addEventListener('touchstart', handleTouch, {passive: false});
canvas.addEventListener('touchmove', handleTouch, {passive: false});
canvas.addEventListener('touchend', () => {
    // Detener movimiento al soltar (opcional, aquí lo manejamos por posición)
    keys['TouchP1Up'] = false;
    keys['TouchP1Down'] = false;
    keys['TouchP2Up'] = false;
    keys['TouchP2Down'] = false;
}, {passive: false});

function handleTouch(e) {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    // Limpiar estados táctiles previos
    keys['TouchP1Up'] = false; keys['TouchP1Down'] = false;
    keys['TouchP2Up'] = false; keys['TouchP2Down'] = false;

    for (let i = 0; i < e.touches.length; i++) {
        const touch = e.touches[i];
        const touchX = (touch.clientX - rect.left) * scaleX;
        const touchY = (touch.clientY - rect.top) * scaleY;

        // Lado izquierdo (Jugador 1)
        if (touchX < canvas.width / 2) {
            if (touchY < player1.y + paddleHeight / 2) keys['TouchP1Up'] = true;
            else keys['TouchP1Down'] = true;
        } 
        // Lado derecho (Jugador 2)
        else if (mode === 'pvp') {
            if (touchY < player2.y + paddleHeight / 2) keys['TouchP2Up'] = true;
            else keys['TouchP2Down'] = true;
        }
    }
}

document.getElementById('btn-ia').onclick = () => start('ia');
document.getElementById('btn-pvp').onclick = () => start('pvp');

function start(m) {
    mode = m;
    gameRunning = true;
    player1.score = player2.score = 0;
    player1.y = player2.y = 160;
    resetBall();
    status.textContent = mode === 'ia' ? "vs IA" : "vs Jugador 2";
    status.style.color = "white";
    requestAnimationFrame(update);
}

function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.dx = (Math.random() > 0.5 ? 4 : -4);
    ball.dy = (Math.random() > 0.5 ? 3 : -3);
}

function checkWinner() {
    if (player1.score >= WINNING_SCORE) {
        gameRunning = false;
        status.textContent = "¡JUGADOR 1 GANA! 🎉";
        status.style.color = "#00ff88";
    } else if (player2.score >= WINNING_SCORE) {
        gameRunning = false;
        status.textContent = mode === 'ia' ? "¡LA IA GANA! 🤖" : "¡JUGADOR 2 GANA! 🎉";
        status.style.color = "#f44336";
    }
}

function update() {
    if (!gameRunning) return;

    // Movimiento Jugador 1 (Teclado o Táctil)
    if ((keys['KeyW'] || keys['TouchP1Up']) && player1.y > 0) player1.y -= 6;
    if ((keys['KeyS'] || keys['TouchP1Down']) && player1.y < canvas.height - paddleHeight) player1.y += 6;

    // Movimiento Jugador 2 (Teclado, Táctil o IA)
    if (mode === 'pvp') {
        if ((keys['ArrowUp'] || keys['TouchP2Up']) && player2.y > 0) player2.y -= 6;
        if ((keys['ArrowDown'] || keys['TouchP2Down']) && player2.y < canvas.height - paddleHeight) player2.y += 6;
    } else {
        const target = ball.y - paddleHeight / 2;
        if (player2.y < target - 5) player2.y += 4;
        if (player2.y > target + 5) player2.y -= 4;
    }

    ball.x += ball.dx;
    ball.y += ball.dy;

    if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) ball.dy *= -1;

    if (ball.x - ball.radius < player1.x + paddleWidth && ball.y > player1.y && ball.y < player1.y + paddleHeight) {
        ball.dx *= -1.05;
        ball.x = player1.x + paddleWidth + ball.radius;
    }
    if (ball.x + ball.radius > player2.x && ball.y > player2.y && ball.y < player2.y + paddleHeight) {
        ball.dx *= -1.05;
        ball.x = player2.x - ball.radius;
    }

    if (ball.x < 0) { player2.score++; resetBall(); checkWinner(); }
    if (ball.x > canvas.width) { player1.score++; resetBall(); checkWinner(); }

    draw();
    if (gameRunning) requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.setLineDash([10, 10]);
    ctx.strokeStyle = 'rgba(255,255,255,0.2)';
    ctx.beginPath();
    ctx.moveTo(canvas.width/2, 0); ctx.lineTo(canvas.width/2, canvas.height);
    ctx.stroke();

    ctx.fillStyle = '#fff';
    ctx.fillRect(player1.x, player1.y, paddleWidth, paddleHeight);
    ctx.fillRect(player2.x, player2.y, paddleWidth, paddleHeight);

    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.font = '30px Orbitron';
    ctx.fillText(player1.score, 200, 50);
    ctx.fillText(player2.score, 600, 50);
}
