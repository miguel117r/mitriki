import os
import uuid
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Configuracion de carpetas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'web_frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

print(f"--- Servidor Mitriki iniciado ---")
print(f"Carpeta frontend: {FRONTEND_DIR}")

games = {}

# --- LOGICA TRIKI ---
class TrikiOnline:
    def __init__(self, vs_ai=False):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.players = {}
        self.current_turn = "X"; self.game_over = False; self.winner = None; self.scores = {"X": 0, "O": 0}
        self.vs_ai = vs_ai
    def restart(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]; self.current_turn = "X"; self.game_over = False; self.winner = None
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
            if self.vs_ai and not self.game_over: self._ai_move()
        return True
    def _ai_move(self):
        move = self._find_best_move("O") or self._find_best_move("X")
        if not move:
            empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
            if empty: move = random.choice(empty)
        if move:
            r, c = move; self.board[r][c] = "O"
            if self._check_winner("O"): self.game_over, self.winner = True, "O"; self.scores["O"] += 1
            elif all(self.board[i][j] != "" for i in range(3) for j in range(3)): self.game_over = True
            else: self.current_turn = "X"
    def _find_best_move(self, p):
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = p
                    win = self._check_winner(p); self.board[r][c] = ""
                    if win: return (r, c)
        return None
    def _check_winner(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)) or all(self.board[j][i] == p for j in range(3)): return True
        return all(self.board[i][i] == p for i in range(3)) or all(self.board[i][2-i] == p for i in range(3))
    def get_state(self, pid):
        return {"board": self.board, "turn": self.current_turn, "role": self.players.get(pid), "game_over": self.game_over, "winner": self.winner, "scores": self.scores, "vs_ai": self.vs_ai}

# --- LÓGICA BUSCAMINAS ---
class Minesweeper:
    def __init__(self, rows=10, cols=10, mines_count=15):
        self.rows, self.cols, self.mines_count = rows, cols, mines_count
        self.board = [["" for _ in range(cols)] for _ in range(rows)]
        self.visible = [["hidden" for _ in range(cols)] for _ in range(rows)]
        self.mines = set(random.sample([(r, c) for r in range(rows) for c in range(cols)], min(mines_count, rows*cols-1)))
        for r, c in self.mines: self.board[r][c] = "M"
        self.game_over, self.winner = False, False
    def reveal(self, r, c):
        if self.game_over or self.visible[r][c] != "hidden": return False
        if (r, c) in self.mines: self.game_over, self.visible[r][c] = True, "revealed"; return True
        self._recursive_reveal(r, c)
        hidden_count = sum(row.count("hidden") + row.count("flagged") for row in self.visible)
        if hidden_count == len(self.mines): self.game_over, self.winner = True, True
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

# --- RUTAS API ---
@app.route('/api/triki/create_room', methods=['POST'])
def triki_create():
    rid = str(random.randint(1000, 9999)); pid = str(uuid.uuid4()); games[rid] = TrikiOnline(vs_ai=False)
    return jsonify({"room_id": rid, "player_id": pid, "role": games[rid].add_player(pid)}), 201

@app.route('/api/triki/create_ai_game', methods=['POST'])
def triki_ai():
    rid = "AI-" + str(random.randint(1000, 9999)); pid = "PLAYER-1"; games[rid] = TrikiOnline(vs_ai=True)
    return jsonify({"room_id": rid, "player_id": pid, "role": games[rid].add_player(pid)}), 201

@app.route('/api/triki/join_room', methods=['POST'])
def triki_join():
    rid = request.json.get('room_id'); pid = str(uuid.uuid4())
    if rid not in games or games[rid].vs_ai: return jsonify({"error": "No"}), 404
    role = games[rid].add_player(pid)
    return jsonify({"room_id": rid, "player_id": pid, "role": role}) if role else (jsonify({"error": "Full"}), 400)

@app.route('/api/triki/<rid>/state/<pid>', methods=['GET'])
def triki_st(rid, pid):
    g = games.get(rid); return jsonify(g.get_state(pid)) if g else ({}, 404)

@app.route('/api/triki/<rid>/move', methods=['POST'])
def triki_mv(rid):
    g = games.get(rid); d = request.json
    if g: g.make_move(d['row'], d['col'], d['role'])
    return jsonify(g.get_state(d['player_id'])) if g else ({}, 404)

@app.route('/api/triki/<rid>/restart', methods=['POST'])
def triki_rs(rid):
    if rid in games: games[rid].restart()
    return jsonify({"ok": True}), 200

@app.route('/api/minesweeper/new_game', methods=['POST'])
def ms_new():
    d = request.json or {}
    r, c, m = d.get('rows', 10), d.get('cols', 10), d.get('mines', 15)
    gid = str(uuid.uuid4()); games[gid] = Minesweeper(r, c, m)
    return jsonify({"game_id": gid, "initial_state": games[gid].get_state()}), 201

@app.route('/api/minesweeper/<gid>/reveal', methods=['POST'])
def ms_rev(gid):
    g = games.get(gid); d = request.json
    if g: g.reveal(d['row'], d['col'])
    return jsonify(g.get_state()) if g else ({}, 404)

@app.route('/api/minesweeper/<gid>/flag', methods=['POST'])
def ms_fl(gid):
    g = games.get(gid); d = request.json
    if g: g.toggle_flag(d['row'], d['col'])
    return jsonify(g.get_state()) if g else ({}, 404)

@app.route('/api/snake/score', methods=['POST'])
def snk_sc(): return jsonify({"ok": True}), 200

# --- RUTAS FRONTEND ---
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    # Intentar servir el archivo desde FRONTEND_DIR
    full_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, path)
    
    # Si es una carpeta de juego o ruta desconocida, intentar buscar el .html o volver al index
    if not path.endswith('.html') and os.path.isfile(full_path + '.html'):
        return send_from_directory(FRONTEND_DIR, path + '.html')
        
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
