// snake.js
const canvas = document.getElementById('snakeCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('current-score');
const highScoreElement = document.getElementById('high-score');
const startButton = document.getElementById('start-button');

const gridSize = 20;
const tileCount = canvas.width / gridSize;

let score = 0;
let highScore = localStorage.getItem('snakeHighScore') || 0;
highScoreElement.textContent = highScore;

let snake = [{x: 10, y: 10}];
let food = {x: 5, y: 5};
let dx = 0, dy = 0;
let nextDx = 0, nextDy = 0;
let gameInterval = null;

// Controles de teclado
window.addEventListener('keydown', e => {
    if (e.key === 'ArrowUp' && dy === 0) { nextDx = 0; nextDy = -1; }
    if (e.key === 'ArrowDown' && dy === 0) { nextDx = 0; nextDy = 1; }
    if (e.key === 'ArrowLeft' && dx === 0) { nextDx = -1; nextDy = 0; }
    if (e.key === 'ArrowRight' && dx === 0) { nextDx = 1; nextDy = 0; }
});

// Controles táctiles (Swipe)
let touchStartX = 0, touchStartY = 0;
canvas.addEventListener('touchstart', e => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
}, {passive: false});

canvas.addEventListener('touchmove', e => e.preventDefault(), {passive: false});

canvas.addEventListener('touchend', e => {
    const touchEndX = e.changedTouches[0].clientX;
    const touchEndY = e.changedTouches[0].clientY;
    const diffX = touchEndX - touchStartX;
    const diffY = touchEndY - touchStartY;

    if (Math.abs(diffX) > Math.abs(diffY)) {
        if (diffX > 30 && dx === 0) { nextDx = 1; nextDy = 0; }
        else if (diffX < -30 && dx === 0) { nextDx = -1; nextDy = 0; }
    } else {
        if (diffY > 30 && dy === 0) { nextDx = 0; nextDy = 1; }
        else if (diffY < -30 && dy === 0) { nextDx = 0; nextDy = -1; }
    }
});

startButton.onclick = startGame;

function startGame() {
    score = 0;
    scoreElement.textContent = score;
    snake = [{x: 10, y: 10}];
    nextDx = 1; nextDy = 0;
    placeFood();
    if (gameInterval) clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, 100);
    startButton.style.display = 'none';
}

function gameLoop() {
    dx = nextDx; dy = nextDy;
    const head = {x: snake[0].x + dx, y: snake[0].y + dy};

    // Colisiones con paredes
    if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) return gameOver();

    // Colisión con sí misma
    if (snake.some(segment => segment.x === head.x && segment.y === head.y)) return gameOver();

    snake.unshift(head);

    // Comer comida
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreElement.textContent = score;
        placeFood();
    } else {
        snake.pop();
    }

    draw();
}

function placeFood() {
    food = {
        x: Math.floor(Math.random() * tileCount),
        y: Math.floor(Math.random() * tileCount)
    };
    // Asegurar que la comida no aparezca sobre la serpiente
    if (snake.some(s => s.x === food.x && s.y === food.y)) placeFood();
}

function gameOver() {
    clearInterval(gameInterval);
    if (score > highScore) {
        highScore = score;
        localStorage.setItem('snakeHighScore', highScore);
        highScoreElement.textContent = highScore;
        fetch('/api/snake/score', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({score: highScore})
        });
    }
    alert(`Game Over! Puntos: ${score}`);
    startButton.style.display = 'block';
    startButton.textContent = 'Reintentar';
}

function draw() {
    ctx.fillStyle = '#0b0e14';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Dibujar comida
    ctx.fillStyle = '#ff0055';
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#ff0055';
    ctx.fillRect(food.x * gridSize + 2, food.y * gridSize + 2, gridSize - 4, gridSize - 4);

    // Dibujar serpiente
    ctx.fillStyle = '#00ff88';
    ctx.shadowColor = '#00ff88';
    snake.forEach((segment, index) => {
        ctx.shadowBlur = index === 0 ? 20 : 5;
        ctx.fillRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2);
    });
    ctx.shadowBlur = 0;
}
