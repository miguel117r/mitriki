# triki_microservice/app.py
import os
import uuid
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Configuración de rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(current_dir, '..', 'web_frontend'))

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app) 

games = {}

# --- Lógica de Triki ---
class TrikiGameLogic:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None

    def make_move(self, row, col, player):
        if self.game_over: return False, "Game over."
        if player != self.current_player: return False, "Not your turn."
        if self.board[row][col] != "": return False, "Cell taken."
        self.board[row][col] = player
        if self._check_winner(player):
            self.game_over = True
            self.winner = player
            return True, f"Player {player} wins!"
        elif all(self.board[i][j] != "" for i in range(3) for j in range(3)):
            self.game_over = True
            return True, "Draw!"
        self.current_player = "O" if player == "X" else "X"
        return True, "Success"

    def _check_winner(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)) or all(self.board[j][i] == p for j in range(3)): return True
        if all(self.board[i][i] == p for i in range(3)) or all(self.board[i][2-i] == p for i in range(3)): return True
        return False

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
            self.game_over = True
            self.visible[r][c] = "revealed"
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
        if self.game_over: return
        if self.visible[r][c] == "hidden": self.visible[r][c] = "flagged"
        elif self.visible[r][c] == "flagged": self.visible[r][c] = "hidden"

    def get_state(self):
        return {
            "visible": self.visible,
            "values": [[self.board[r][c] if self.visible[r][c] == "revealed" else "" for c in range(self.cols)] for r in range(self.rows)],
            "game_over": self.game_over, "winner": self.winner, "rows": self.rows, "cols": self.cols
        }

# --- Rutas API ---
@app.route('/api/triki/new_game', methods=['POST'])
def triki_new():
    gid = str(uuid.uuid4())
    games[gid] = TrikiGameLogic()
    return jsonify({"game_id": gid, "initial_state": games[gid].get_state()}), 201

@app.route('/api/triki/<gid>/move', methods=['POST'])
def triki_move(gid):
    g = games.get(gid)
    if not g: return jsonify({"error": "Game not found"}), 404
    data = request.json
    success, msg = g.make_move(data.get('row'), data.get('col'), data.get('player'))
    return jsonify({"message": msg, "new_state": g.get_state()}), 200 if success else 400

@app.route('/api/minesweeper/new_game', methods=['POST'])
def mine_new():
    gid = str(uuid.uuid4())
    games[gid] = MinesweeperGameLogic()
    return jsonify({"game_id": gid, "initial_state": games[gid].get_state()}), 201

@app.route('/api/minesweeper/<gid>/reveal', methods=['POST'])
def mine_reveal(gid):
    g = games.get(gid)
    if not g: return jsonify({"error": "Game not found"}), 404
    data = request.json
    g.reveal(data.get('row'), data.get('col'))
    return jsonify(g.get_state()), 200

@app.route('/api/minesweeper/<gid>/flag', methods=['POST'])
def mine_flag(gid):
    g = games.get(gid)
    if not g: return jsonify({"error": "Game not found"}), 404
    data = request.json
    g.toggle_flag(data.get('row'), data.get('col'))
    return jsonify(g.get_state()), 200

# Rutas de archivos estáticos
@app.route('/')
def serve_index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/games/<path:filename>')
def serve_game_html(filename):
    return send_from_directory(os.path.join(frontend_dir, 'games'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(frontend_dir, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(frontend_dir, 'js'), filename)

if __name__ == '__main__':
    # Usar puerto de Render o 5000 por defecto
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
