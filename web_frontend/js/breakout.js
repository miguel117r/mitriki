const canvas = document.getElementById("breakout");
const ctx = canvas.getContext("2d");
const scoreDisplay = document.getElementById("score");
const livesDisplay = document.getElementById("lives");
const levelDisplay = document.getElementById("level");

let score = 0;
let lives = 3;
let level = 1;
let paused = false;
let gameOver = false;

// Propiedades de la bola
let ballRadius = 8;
let x = canvas.width / 2;
let y = canvas.height - 30;
let baseSpeed = 4;
let dx = baseSpeed;
let dy = -baseSpeed;

// Propiedades de la paleta
const paddleHeight = 12;
const paddleWidth = 100;
let paddleX = (canvas.width - paddleWidth) / 2;

// Configuración de ladrillos dinámica
let brickRowCount = 4;
let brickColumnCount = 8;
const brickWidth = 80;
const brickHeight = 25;
const brickPadding = 12;
const brickOffsetTop = 50;
const brickOffsetLeft = 40;

let bricks = [];

function initBricks() {
    brickRowCount = 3 + level; // Más filas según el nivel
    const totalBrickWidth = (brickColumnCount * (brickWidth + brickPadding)) - brickPadding;
    const startX = (canvas.width - totalBrickWidth) / 2;
    
    bricks = [];
    for (let c = 0; c < brickColumnCount; c++) {
        bricks[c] = [];
        for (let r = 0; r < brickRowCount; r++) {
            // Ladrillos con diferentes colores según la fila
            let color = `hsl(${200 + (r * 30)}, 100%, 50%)`;
            bricks[c][r] = { x: 0, y: 0, status: 1, color: color };
        }
    }
}

initBricks();

document.addEventListener("mousemove", mouseMoveHandler, false);
document.addEventListener("keydown", (e) => {
    if (e.key.toLowerCase() === 'r') document.location.reload();
});

function mouseMoveHandler(e) {
    let relativeX = e.clientX - canvas.getBoundingClientRect().left;
    if (relativeX > 0 && relativeX < canvas.width) {
        paddleX = relativeX - paddleWidth / 2;
    }
}

function collisionDetection() {
    let activeBricks = 0;
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            let b = bricks[c][r];
            if (b.status === 1) {
                activeBricks++;
                if (x > b.x && x < b.x + brickWidth && y > b.y && y < b.y + brickHeight) {
                    dy = -dy;
                    b.status = 0;
                    score += 10;
                    scoreDisplay.innerText = score;
                }
            }
        }
    }
    
    if (activeBricks === 0 && !gameOver) {
        nextLevel();
    }
}

function nextLevel() {
    level++;
    levelDisplay.innerText = level;
    baseSpeed += 0.5;
    resetBall();
    initBricks();
}

function resetBall() {
    x = canvas.width / 2;
    y = canvas.height - 30;
    dx = baseSpeed * (Math.random() > 0.5 ? 1 : -1);
    dy = -baseSpeed;
    paddleX = (canvas.width - paddleWidth) / 2;
}

function drawBall() {
    ctx.beginPath();
    ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.shadowBlur = 10;
    ctx.shadowColor = "#ffffff";
    ctx.fill();
    ctx.closePath();
    ctx.shadowBlur = 0; // Reset shadow
}

function drawPaddle() {
    ctx.beginPath();
    ctx.roundRect(paddleX, canvas.height - paddleHeight - 5, paddleWidth, paddleHeight, 5);
    ctx.fillStyle = "#00ff88";
    ctx.fill();
    ctx.closePath();
}

function drawBricks() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            if (bricks[c][r].status === 1) {
                let brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                let brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                bricks[c][r].x = brickX;
                bricks[c][r].y = brickY;
                ctx.beginPath();
                ctx.roundRect(brickX, brickY, brickWidth, brickHeight, 3);
                ctx.fillStyle = bricks[c][r].color;
                ctx.fill();
                ctx.closePath();
            }
        }
    }
}

function drawMessage(text, subtext) {
    ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.font = "bold 40px Orbitron, sans-serif";
    ctx.fillStyle = "#00ff88";
    ctx.textAlign = "center";
    ctx.fillText(text, canvas.width/2, canvas.height/2);
    
    ctx.font = "20px Inter, sans-serif";
    ctx.fillStyle = "#ffffff";
    ctx.fillText(subtext, canvas.width/2, canvas.height/2 + 50);
}

function draw() {
    if (gameOver) {
        drawMessage("GAME OVER", "Presiona R para intentar de nuevo");
        return;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBricks();
    drawBall();
    drawPaddle();
    collisionDetection();

    // Rebotes paredes
    if (x + dx > canvas.width - ballRadius || x + dx < ballRadius) dx = -dx;
    if (y + dy < ballRadius) dy = -dy;
    else if (y + dy > canvas.height - ballRadius - 5) {
        if (x > paddleX && x < paddleX + paddleWidth) {
            // Calcular ángulo de rebote según donde toque la paleta
            let hitPoint = (x - (paddleX + paddleWidth / 2)) / (paddleWidth / 2);
            dx = hitPoint * baseSpeed * 1.5;
            dy = -dy;
        } else {
            lives--;
            livesDisplay.innerText = lives;
            if (lives <= 0) {
                gameOver = true;
            } else {
                resetBall();
            }
        }
    }

    x += dx;
    y += dy;
    requestAnimationFrame(draw);
}

draw();
