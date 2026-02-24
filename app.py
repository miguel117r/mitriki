import os
import uuid
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'web_frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

games = {}

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
            if self.vs_ai and not self.game_over:
                self._ai_move()
        return True

    def _ai_move(self):
        # 1. Intentar ganar o bloquear
        move = self._find_best_move("O") or self._find_best_move("X")
        if not move:
            # 2. Si no, elegir al azar de las vacias
            empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
            if empty: move = random.choice(empty)
        
        if move:
            r, c = move
            self.board[r][c] = "O"
            if self._check_winner("O"):
                self.game_over, self.winner = True, "O"
                self.scores["O"] += 1
            elif all(self.board[i][j] != "" for i in range(3) for j in range(3)):
                self.game_over = True
            else:
                self.current_turn = "X"

    def _find_best_move(self, p):
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = p
                    win = self._check_winner(p)
                    self.board[r][c] = ""
                    if win: return (r, c)
        return None

    def _check_winner(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)) or all(self.board[j][i] == p for j in range(3)): return True
        return all(self.board[i][i] == p for i in range(3)) or all(self.board[i][2-i] == p for i in range(3))

    def get_state(self, pid):
        return {"board": self.board, "turn": self.current_turn, "role": self.players.get(pid), "game_over": self.game_over, "winner": self.winner, "scores": self.scores, "vs_ai": self.vs_ai}

@app.route('/api/triki/create_room', methods=['POST'])
def triki_create():
    rid = str(random.randint(1000, 9999)); pid = str(uuid.uuid4()); games[rid] = TrikiOnline(vs_ai=False)
    return jsonify({"room_id": rid, "player_id": pid, "role": games[rid].add_player(pid)}), 201

@app.route('/api/triki/create_ai_game', methods=['POST'])
def triki_ai():
    rid = "AI-" + str(random.randint(1000, 9999)); pid = "PLAYER-1"
    games[rid] = TrikiOnline(vs_ai=True)
    return jsonify({"room_id": rid, "player_id": pid, "role": games[rid].add_player(pid)}), 201

@app.route('/api/triki/join_room', methods=['POST'])
def triki_join():
    rid = request.json.get('room_id'); pid = str(uuid.uuid4())
    if rid not in games or games[rid].vs_ai: return jsonify({"error": "No disponible"}), 404
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

# --- LÓGICA BUSCAMINAS Y OTROS (Mantenidos) ---
# ... (Se mantienen las rutas de minesweeper y archivos estáticos) ...
