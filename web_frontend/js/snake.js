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

// Función global para los botones
window.changeDirection = (dir) => {
    if (dir === 'up' && dy === 0) { nextDx = 0; nextDy = -1; }
    if (dir === 'down' && dy === 0) { nextDx = 0; nextDy = 1; }
    if (dir === 'left' && dx === 0) { nextDx = -1; nextDy = 0; }
    if (dir === 'right' && dx === 0) { nextDx = 1; nextDy = 0; }
};

// Controles de teclado
window.addEventListener('keydown', e => {
    if (e.key === 'ArrowUp') changeDirection('up');
    if (e.key === 'ArrowDown') changeDirection('down');
    if (e.key === 'ArrowLeft') changeDirection('left');
    if (e.key === 'ArrowRight') changeDirection('right');
});

startButton.onclick = startGame;

function startGame() {
    score = 0;
    scoreElement.textContent = score;
    document.getElementById('game-status').textContent = "¡Buena suerte!";
    snake = [{x: 10, y: 10}];
    nextDx = 1; nextDy = 0;
    placeFood();
    if (gameInterval) clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, 120);
    startButton.style.display = 'none';
}

function gameLoop() {
    dx = nextDx; dy = nextDy;
    const head = {x: snake[0].x + dx, y: snake[0].y + dy};

    if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) return gameOver();
    if (snake.some(segment => segment.x === head.x && segment.y === head.y)) return gameOver();

    snake.unshift(head);
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
    if (snake.some(s => s.x === food.x && s.y === food.y)) placeFood();
}

function gameOver() {
    clearInterval(gameInterval);
    const status = document.getElementById('game-status');
    if (score > highScore) {
        highScore = score;
        localStorage.setItem('snakeHighScore', highScore);
        highScoreElement.textContent = highScore;
        status.textContent = `¡NUEVO RÉCORD: ${score}! 🏆`;
    } else {
        status.textContent = `GAME OVER - Puntos: ${score} 💀`;
    }
    startButton.style.display = 'block';
    startButton.textContent = 'Reintentar';
}

function draw() {
    ctx.fillStyle = '#0b0e14';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ff0055';
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#ff0055';
    ctx.fillRect(food.x * gridSize + 2, food.y * gridSize + 2, gridSize - 4, gridSize - 4);
    ctx.fillStyle = '#00ff88';
    ctx.shadowColor = '#00ff88';
    snake.forEach((segment, index) => {
        ctx.shadowBlur = index === 0 ? 20 : 5;
        ctx.fillRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2);
    });
    ctx.shadowBlur = 0;
}
