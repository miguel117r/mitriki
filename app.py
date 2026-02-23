# triki_microservice/app.py
import os
import uuid
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Rutas absolutas
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, 'web_frontend')

# Configuramos Flask para que sirva TODO desde web_frontend automáticamente
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app) 

games = {}

# --- Lógica de Triki ---
class TrikiGameLogic:
    def __init__(self, mode='pvp'):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None
        self.mode = mode

    def make_move(self, row, col, player):
        if self.game_over or self.board[row][col] != "" or player != self.current_player:
            return False, "Movimiento inválido"
        
        self.board[row][col] = player
        if self._check_winner(player):
            self.game_over = True
            self.winner = player
            return True, "Ganaste"
        
        if all(self.board[i][j] != "" for i in range(3) for j in range(3)):
            self.game_over = True
            return True, "Empate"

        self.current_player = "O" if player == "X" else "X"
        if self.mode == 'ia' and self.current_player == "O" and not self.game_over:
            self._ai_move()
        return True, "Ok"

    def _ai_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty:
            r, c = random.choice(empty)
            self.board[r][c] = "O"
            if self._check_winner("O"):
                self.game_over, self.winner = True, "O"
            elif all(self.board[i][j] != "" for i in range(3) for j in range(3)):
                self.game_over = True
            else:
                self.current_player = "X"

    def _check_winner(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)) or all(self.board[j][i] == p for j in range(3)): return True
        return all(self.board[i][i] == p for i in range(3)) or all(self.board[i][2-i] == p for i in range(3))

    def get_state(self):
        return {"board": self.board, "current_player": self.current_player, "game_over": self.game_over, "winner": self.winner}

# --- Lógica de Buscaminas ---
class MinesweeperGameLogic:
    def __init__(self, rows=10, cols=10, mines=15):
        self.rows, self.cols, self.mines_count = rows, cols, mines
        self.board = [["" for _ in range(cols)] for _ in range(rows)]
        self.visible = [["hidden" for _ in range(cols)] for _ in range(rows)]
        self.mines = set(random.sample([(r, c) for r in range(rows) for c in range(cols)], mines))
        for r, c in self.mines: self.board[r][c] = "M"
        self.game_over = False
        self.winner = False

    def reveal(self, r, c):
        if self.game_over or self.visible[r][c] != "hidden": return False
        if (r, c) in self.mines:
            self.game_over, self.visible[r][c] = True, "revealed"
            return True
        self._recursive_reveal(r, c)
        if sum(row.count("hidden") for row in self.visible) == self.mines_count:
            self.game_over, self.winner = True, True
        return True

    def _recursive_reveal(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols) or self.visible[r][c] != "hidden": return
        adj = sum(1 for dr in [-1,0,1] for dc in [-1,0,1] if (r+dr, c+dc) in self.mines)
        self.visible[r][c] = "revealed"
        self.board[r][c] = str(adj)
        if adj == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    if dr != 0 or dc != 0: self._recursive_reveal(r+dr, c+dc)

    def toggle_flag(self, r, c):
        if not self.game_over:
            if self.visible[r][c] == "hidden": self.visible[r][c] = "flagged"
            elif self.visible[r][c] == "flagged": self.visible[r][c] = "hidden"

    def get_state(self):
        return {
            "visible": self.visible,
            "values": [[self.board[r][c] if self.visible[r][c] == "revealed" else "" for c in range(self.cols)] for r in range(self.rows)],
            "game_over": self.game_over, "winner": self.winner, "rows": self.rows, "cols": self.cols
        }

# --- API ---
@app.route('/api/triki/new_game', methods=['POST'])
def triki_new():
    data = request.json or {}; mode = data.get('mode', 'pvp')
    gid = str(uuid.uuid4()); games[gid] = TrikiGameLogic(mode)
    return jsonify({"game_id": gid, "initial_state": games[gid].get_state()}), 201

@app.route('/api/triki/<gid>/state', methods=['GET'])
def triki_state(gid):
    g = games.get(gid)
    return jsonify(g.get_state()) if g else (jsonify({"error": "No encontrado"}), 404)

@app.route('/api/triki/<gid>/move', methods=['POST'])
def triki_move(gid):
    g = games.get(gid); data = request.json
    if not g: return jsonify({"error": "No encontrado"}), 404
    g.make_move(data.get('row'), data.get('col'), data.get('player'))
    return jsonify({"new_state": g.get_state()}), 200

@app.route('/api/minesweeper/new_game', methods=['POST'])
def mine_new():
    gid = str(uuid.uuid4()); games[gid] = MinesweeperGameLogic()
    return jsonify({"game_id": gid, "initial_state": games[gid].get_state()}), 201

@app.route('/api/minesweeper/<gid>/reveal', methods=['POST'])
def mine_reveal(gid):
    g = games.get(gid); data = request.json
    if g: g.reveal(data.get('row'), data.get('col'))
    return jsonify(g.get_state()) if g else (jsonify({"error": "No"}), 404)

@app.route('/api/minesweeper/<gid>/flag', methods=['POST'])
def mine_flag(gid):
    g = games.get(gid); data = request.json
    if g: g.toggle_flag(data.get('row'), data.get('col'))
    return jsonify(g.get_state()) if g else (jsonify({"error": "No"}), 404)

# --- Servir archivos estáticos ---
@app.route('/')
def serve_index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(frontend_dir, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
