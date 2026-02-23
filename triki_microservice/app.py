# triki_microservice/app.py
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# In-memory store for active games
# In a real application, this would be a database or a distributed cache
games = {}

# Construct the path to the web_frontend directory
# Assumes web_frontend and triki_microservice are siblings in the same parent directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_frontend'))

# Configure Flask to serve static files from the web_frontend directory
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app) # Enable CORS for all routes

class TrikiGameLogic:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None

    def make_move(self, row, col, player):
        if self.game_over:
            return False, "Game is over."
        if player != self.current_player:
            return False, "It's not your turn."
        if not (0 <= row < 3 and 0 <= col < 3):
            return False, "Invalid move: Out of bounds."
        if self.board[row][col] != "":
            return False, "Invalid move: Cell already taken."

        self.board[row][col] = player
        
        if self._check_winner(player):
            self.game_over = True
            self.winner = player
            return True, f"Player {player} wins!"
        elif self._check_draw():
            self.game_over = True
            return True, "It's a draw!"
        else:
            self.current_player = "O" if player == "X" else "X"
            return True, "Move successful."

    def _check_winner(self, player):
        # Check rows
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):
                return True
        # Check columns
        for j in range(3):
            if all(self.board[i][j] == player for i in range(3)):
                return True
        # Check diagonals
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def _check_draw(self):
        return all(self.board[i][j] != "" for i in range(3) for j in range(3)) and not self.winner

    def get_state(self):
        return {
            "board": self.board,
            "current_player": self.current_player,
            "game_over": self.game_over,
            "winner": self.winner
        }

# API Endpoints
@app.route('/api/triki/new_game', methods=['POST'])
def new_game():
    game_id = str(uuid.uuid4())
    games[game_id] = TrikiGameLogic()
    return jsonify({"game_id": game_id, "initial_state": games[game_id].get_state()}), 201

@app.route('/api/triki/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"message": "Game not found"}), 404
    return jsonify(game.get_state()), 200

@app.route('/api/triki/<game_id>/move', methods=['POST'])
def make_move(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"message": "Game not found"}), 404

    data = request.get_json()
    row = data.get('row')
    col = data.get('col')
    player = data.get('player')

    if row is None or col is None or player is None:
        return jsonify({"message": "Missing row, col, or player in request"}), 400

    success, message = game.make_move(row, col, player)

    if not success:
        return jsonify({"message": message, "current_state": game.get_state()}), 400
    
    return jsonify({"message": message, "new_state": game.get_state()}), 200

# Serve index.html from the root URL
@app.route('/')
def serve_index():
    return send_from_directory(frontend_dir, 'index.html')

# Serve game-specific HTML files (e.g., triki.html)
@app.route('/games/<path:filename>')
def serve_game_html(filename):
    return send_from_directory(os.path.join(frontend_dir, 'games'), filename)

# Serve CSS files
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(frontend_dir, 'css'), filename)

# Serve JS files
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(frontend_dir, 'js'), filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
