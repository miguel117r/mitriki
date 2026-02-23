import os
import uuid
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='web_frontend', static_url_path='')
CORS(app) 

games = {}

# --- Lógica de Triki Online ---
class TrikiOnline:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.players = {} # { 'player_id': 'X' or 'O' }
        self.current_turn = "X"
        self.game_over = False
        self.winner = None
        self.scores = {"X": 0, "O": 0}

    def restart(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_turn = "X"; self.game_over = False; self.winner = None

    def add_player(self, player_id):
        if len(self.players) >= 2: return None
        role = "X" if not self.players else "O"
        self.players[player_id] = role
        return role

    def make_move(self, row, col, role):
        if self.game_over or self.board[row][col] != "" or role != self.current_turn: return False
        self.board[row][col] = role
        if self._check_winner(role):
            self.game_over, self.winner = True, role
            self.scores[role] += 1
        elif all(self.board[i][j] != "" for i in range(3) for j in range(3)): self.game_over = True
        else: self.current_turn = "O" if role == "X" else "X"
        return True

    def _check_winner(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)) or all(self.board[j][i] == p for j in range(3)): return True
        return all(self.board[i][i] == p for i in range(3)) or all(self.board[i][2-i] == p for i in range(3))

    def get_state(self, player_id):
        return {"board": self.board, "turn": self.current_turn, "role": self.players.get(player_id), "players_count": len(self.players), "game_over": self.game_over, "winner": self.winner, "scores": self.scores}

# --- Lógica de Buscaminas ---
class MinesweeperGameLogic:
    def __init__(self, rows=10, cols=10, mines=15):
        self.rows, self.cols, self.mines_count = rows, cols, mines
        self.board = [["" for _ in range(cols)] for _ in range(rows)]
        self.visible = [["hidden" for _ in range(cols)] for _ in range(rows)]
        self.mines = set(random.sample([(r, c) for r in range(rows) for c in range(cols)], mines))
        for r, c in self.mines: self.board[r][c] = "M"
        self.game_over, self.winner = False, False

    def reveal(self, r, c):
        if self.game_over or self.visible[r][c] != "hidden": return False
        if (r, c) in self.mines: self.game_over, self.visible[r][c] = True, "revealed"; return True
        self._recursive_reveal(r, c)
        if sum(row.count("hidden") for row in self.visible) == self.mines_count: self.game_over, self.winner = True, True
        return True

    def _recursive_reveal(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols) or self.visible[r][c] != "hidden": return
        adj = sum(1 for dr in [-1,0,1] for dc in [-1,0,1] if (r+dr, c+dc) in self.mines)
        self.visible[r][c] = "revealed"; self.board[r][c] = str(adj)
        if adj == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    if dr != 0 or dc != 0: self._recursive_reveal(r+dr, c+dc)

    def toggle_flag(self, r, c):
        if not self.game_over:
            if self.visible[r][c] == "hidden": self.visible[r][c] = "flagged"
            elif self.visible[r][c] == "flagged": self.visible[r][c] = "hidden"

    def get_state(self):
        return {"visible": self.visible, "values": [[self.board[r][c] if self.visible[r][c] == "revealed" else "" for c in range(self.cols)] for r in range(self.rows)], "game_over": self.game_over, "winner": self.winner, "rows": self.rows, "cols": self.cols}

# --- Rutas API ---
@app.route('/api/triki/create_room', methods=['POST'])
def create_room():
    rid = str(random.randint(1000, 9999)); pid = str(uuid.uuid4()); games[rid] = TrikiOnline()
    role = games[rid].add_player(pid)
    return jsonify({"room_id": rid, "player_id": pid, "role": role}), 201

@app.route('/api/triki/join_room', methods=['POST'])
def join_room():
    rid = request.json.get('room_id'); pid = str(uuid.uuid4())
    if rid not in games: return jsonify({"error": "No found"}), 404
    role = games[rid].add_player(pid)
    return jsonify({"room_id": rid, "player_id": pid, "role": role}) if role else (jsonify({"error": "Full"}), 400)

@app.route('/api/triki/<rid>/move', methods=['POST'])
def triki_move(rid):
    g = games.get(rid); d = request.json
    success = g.make_move(d['row'], d['col'], d['role'])
    return jsonify(g.get_state(d['player_id'])), 200 if success else 400

@app.route('/api/triki/<rid>/state/<pid>', methods=['GET'])
def triki_state(rid, pid):
    g = games.get(rid); return jsonify(g.get_state(pid)) if g else (jsonify({"error": "No"}), 404)

@app.route('/api/triki/<rid>/restart', methods=['POST'])
def triki_restart(rid):
    if rid in games: games[rid].restart()
    return jsonify({"status": "ok"}), 200

@app.route('/api/minesweeper/new_game', methods=['POST'])
def mine_new():
    gid = str(uuid.uuid4()); games[gid] = MinesweeperGameLogic()
    return jsonify({"game_id": gid, "initial_state": games[gid].get_state()}), 201

@app.route('/api/minesweeper/<gid>/reveal', methods=['POST'])
def mine_reveal(gid):
    g = games.get(gid); d = request.json
    if g: g.reveal(d['row'], d['col'])
    return jsonify(g.get_state()) if g else ({}, 404)

@app.route('/api/snake/score', methods=['POST'])
def snake_score():
    print(f"Snake Score: {request.json}"); return jsonify({"status": "ok"}), 200

@app.route('/')
def index(): return send_from_directory('web_frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path): return send_from_directory('web_frontend', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
