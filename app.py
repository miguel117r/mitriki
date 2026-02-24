import os
import uuid
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Configuracion de carpetas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'web_frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

games = {}

# --- LOGICA TRIKI ONLINE ---
class TrikiOnline:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.players = {}
        self.current_turn = "X"
        self.game_over = False
        self.winner = None
        self.scores = {"X": 0, "O": 0}

    def restart(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_turn = "X"
        self.game_over = False
        self.winner = None

    def add_player(self, pid):
        if len(self.players) >= 2: return None
        role = "X" if not self.players else "O"
        self.players[pid] = role
        return role

    def make_move(self, r, c, role):
        if self.game_over or self.board[r][c] != "" or role != self.current_turn: return False
        self.board[r][c] = role
        if self._check_winner(role):
            self.game_over, self.winner = True, role
            self.scores[role] += 1
        elif all(self.board[i][j] != "" for i in range(3) for j in range(3)):
            self.game_over = True       
        else:
            self.current_turn = "O" if role == "X" else "X"
        return True

    def _check_winner(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)) or all(self.board[j][i] == p for j in range(3)): return True
        return all(self.board[i][i] == p for i in range(3)) or all(self.board[i][2-i] == p for i in range(3))

    def get_state(self, pid):
        return {
            "board": self.board, 
            "turn": self.current_turn, 
            "role": self.players.get(pid), 
            "players_count": len(self.players), 
            "game_over": self.game_over, 
            "winner": self.winner, 
            "scores": self.scores
        }       

# --- LOGICA BUSCAMINAS ---
class Minesweeper:
    def __init__(self):
        self.rows, self.cols, self.mines_count = 10, 10, 15
        self.board = [["" for _ in range(10)] for _ in range(10)]
        self.visible = [["hidden" for _ in range(10)] for _ in range(10)]
        self.mines = set(random.sample([(r, c) for r in range(10) for c in range(10)], 15))
        for r, c in self.mines: self.board[r][c] = "M"
        self.game_over, self.winner = False, False

    def reveal(self, r, c):
        if self.game_over or self.visible[r][c] != "hidden": return False
        if (r, c) in self.mines:
            self.game_over, self.visible[r][c] = True, "revealed"
            return True       
        self._recursive_reveal(r, c)
        if sum(row.count("hidden") for row in self.visible) == 15:
            self.game_over, self.winner = True, True
        return True

    def _recursive_reveal(self, r, c):
        if not (0 <= r < 10 and 0 <= c < 10) or self.visible[r][c] != "hidden": return
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
            "values": [[self.board[r][c] if self.visible[r][c] == "revealed" else "" for c in range(10)] for r in range(10)], 
            "game_over": self.game_over, 
            "winner": self.winner, 
            "rows": 10, 
            "cols": 10
        }

# --- RUTAS DE LA API ---
@app.route('/api/triki/create_room', methods=['POST'])
def triki_create():
    rid = str(random.randint(1000, 9999))
    pid = str(uuid.uuid4())
    games[rid] = TrikiOnline()
    return jsonify({"room_id": rid, "player_id": pid, "role": games[rid].add_player(pid)}), 201

@app.route('/api/triki/join_room', methods=['POST'])
def triki_join():
    rid = request.json.get('room_id')
    pid = str(uuid.uuid4())
    if rid not in games: return jsonify({"error": "No existe la sala"}), 404
    role = games[rid].add_player(pid)
    if not role: return jsonify({"error": "Sala llena"}), 400
    return jsonify({"room_id": rid, "player_id": pid, "role": role})

@app.route('/api/triki/<rid>/state/<pid>', methods=['GET'])
def triki_st(rid, pid):
    g = games.get(rid)
    if not g: return jsonify({"error": "Sala no encontrada"}), 404
    return jsonify(g.get_state(pid))

@app.route('/api/triki/<rid>/move', methods=['POST'])
def triki_mv(rid):
    g = games.get(rid)
    if not g: return jsonify({"error": "Sala no encontrada"}), 404
    d = request.json
    g.make_move(d['row'], d['col'], d['role'])
    return jsonify(g.get_state(d['player_id']))

@app.route('/api/triki/<rid>/restart', methods=['POST'])
def triki_rs(rid):
    if rid in games:
        games[rid].restart()
        return jsonify({"ok": True}), 200
    return jsonify({"error": "Sala no encontrada"}), 404

@app.route('/api/minesweeper/new_game', methods=['POST'])
def ms_new():
    gid = str(uuid.uuid4())
    games[gid] = Minesweeper()
    return jsonify({"game_id": gid, "initial_state": games[gid].get_state()}), 201

@app.route('/api/minesweeper/<gid>/reveal', methods=['POST'])
def ms_rev(gid):
    g = games.get(gid)
    if not g: return jsonify({"error": "Juego no encontrado"}), 404
    d = request.json
    g.reveal(d['row'], d['col'])
    return jsonify(g.get_state())

# --- RUTAS PARA EL FRONTEND ---
@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor iniciado en el puerto {port}")
    app.run(host='0.0.0.0', port=port)
