# -*- coding: utf-8 -*- 

# multigame_app.py
# Autor: Gemini
# Fecha: 2026-02-03
# Descripción: Una aplicación de multijuegos con Triki y Buscaminas.

import tkinter as tk
from tkinter import messagebox
import random

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Juego")
        self.root.geometry("400x550")
        self.current_game_frame = None
        self.show_main_menu()

    def show_main_menu(self):
        if self.current_game_frame:
            self.current_game_frame.destroy()
            self.current_game_frame = None
            
        self.root.title("Multi-Juego")
        self.main_menu_frame = tk.Frame(self.root)
        self.main_menu_frame.pack(pady=20)

        title_label = tk.Label(self.main_menu_frame, text="Selecciona un Juego", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)

        triki_button = tk.Button(self.main_menu_frame, text="Tres en Línea (Triki)", font=("Arial", 16), command=self.start_triki)
        triki_button.pack(pady=10)

        minesweeper_button = tk.Button(self.main_menu_frame, text="Buscaminas", font=("Arial", 16), command=self.start_minesweeper)
        minesweeper_button.pack(pady=10)
        
        pong_button = tk.Button(self.main_menu_frame, text="Pong", font=("Arial", 16), command=self.start_pong)
        pong_button.pack(pady=10)

    def start_triki(self):
        self.main_menu_frame.destroy()
        self.current_game_frame = tk.Frame(self.root)
        self.current_game_frame.pack()
        TrikiGame(self.current_game_frame, self.show_main_menu)

    def start_minesweeper(self):
        self.main_menu_frame.destroy()
        self.current_game_frame = tk.Frame(self.root)
        self.current_game_frame.pack()
        MinesweeperGame(self.current_game_frame, self.show_main_menu)
        
    def start_pong(self):
        self.main_menu_frame.destroy()
        self.current_game_frame = tk.Frame(self.root)
        self.current_game_frame.pack()
        PongGame(self.current_game_frame, self.show_main_menu)

class PongGame:
    def __init__(self, parent_frame, show_main_menu_callback):
        self.parent_frame = parent_frame
        self.show_main_menu_callback = show_main_menu_callback
        
        self.main_frame = tk.Frame(parent_frame)
        self.main_frame.pack()

        self.canvas = tk.Canvas(self.main_frame, width=600, height=400, bg="black")
        # Canvas is packed only when game mode is selected
        
        self.score_player1 = 0
        self.score_player2 = 0
        self.max_score = 10
        self.game_running = False
        self.game_mode = None # "PVP" o "PVC"

        # Frame for mode selection
        self.mode_selection_frame = tk.Frame(self.main_frame)
        self.mode_selection_frame.pack(pady=20)
        
        mode_label = tk.Label(self.mode_selection_frame, text="Selecciona un modo de juego:", font=("Arial", 16))
        mode_label.pack(pady=10)

        pvp_button = tk.Button(self.mode_selection_frame, text="Jugador vs Jugador", font=("Arial", 14), command=lambda: self.start_game_mode("PVP"))
        pvp_button.pack(pady=5)

        pvc_button = tk.Button(self.mode_selection_frame, text="Jugador vs PC", font=("Arial", 14), command=lambda: self.start_game_mode("PVC"))
        pvc_button.pack(pady=5)
        
        back_button = tk.Button(self.mode_selection_frame, text="Volver al Menú Principal", font=("Arial", 10), command=self.go_to_main_menu)
        back_button.pack(pady=20)

        self.initial_ball_speed = 5
        self.ball_speed_increment = 0.5
        self.paddle_speed = 15

        self.game_elements_created = False
        self.game_canvas_id = None
        self.player2_paddle = None
        self.pc_paddle_id = None
        self.player_paddle = None # Initialize to None, will be created in _create_game_elements
        self.ball = None # Initialize to None, will be created in _create_game_elements
        self.score_display = None # Initialize to None, will be created in _create_game_elements
        
        # Movement state variables
        self.player1_move = 0  # -1 for up, 1 for down, 0 for still
        self.player2_move = 0  # -1 for up, 1 for down, 0 for still

        self.game_loop_id = None # To store the ID of the scheduled game_loop call

    def game_loop(self):
        if not self.game_running:
            return
        
        # Ensure critical game elements are initialized
        if not self.ball or not self.player_paddle:
            return

        self.move_ball()
        self.move_paddles()
        if self.game_mode == "PVC":
            self.move_pc_paddle()
        self.game_loop_id = self.parent_frame.after(20, self.game_loop) # Update every 20ms

    def _create_game_elements(self):
        if self.game_elements_created:
            return

        self.game_canvas_id = self.canvas.create_rectangle(0, 0, 600, 400, fill="black")

        self.player_paddle = self.canvas.create_rectangle(50, 150, 65, 250, fill="white")
        self.ball = self.canvas.create_oval(290, 190, 310, 210, fill="white")
        self.score_display = self.canvas.create_text(300, 50, text="0 - 0", fill="white", font=("Arial", 30))

        if self.game_mode == "PVC":
            self.pc_paddle_id = self.canvas.create_rectangle(535, 150, 550, 250, fill="white")
        elif self.game_mode == "PVP":
            self.player2_paddle = self.canvas.create_rectangle(535, 150, 550, 250, fill="white")
        
        self.game_elements_created = True

    def start_game_mode(self, mode):
        self.game_mode = mode
        self.mode_selection_frame.pack_forget() # Hide mode selection
        
        # Display game elements
        self.canvas.pack()
        self._create_game_elements()

        # Add buttons for game control
        self.start_button = tk.Button(self.main_frame, text="Iniciar Juego", command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.reset_mode_button = tk.Button(self.main_frame, text="Cambiar de Modo", command=self.reset_game_mode)
        self.reset_mode_button.pack(pady=5)

        self.back_button = tk.Button(self.main_frame, text="Volver al Menú Principal", command=self.go_to_main_menu)
        self.back_button.pack(pady=5)
        
        self.reset_game()

        self.parent_frame.bind("<KeyPress>", self._on_key_press)
        self.parent_frame.bind("<KeyRelease>", self._on_key_release)
        self.parent_frame.focus_set()
        
    def _on_key_press(self, event):
        if event.keysym == 'w':
            self.player1_move = -1
        elif event.keysym == 's':
            self.player1_move = 1
        elif self.game_mode == "PVP":
            if event.keysym == 'Up':
                self.player2_move = -1
            elif event.keysym == 'Down':
                self.player2_move = 1

    def _on_key_release(self, event):
        if event.keysym == 'w' and self.player1_move == -1:
            self.player1_move = 0
        elif event.keysym == 's' and self.player1_move == 1:
            self.player1_move = 0
        elif self.game_mode == "PVP":
            if event.keysym == 'Up' and self.player2_move == -1:
                self.player2_move = 0
            elif event.keysym == 'Down' and self.player2_move == 1:
                self.player2_move = 0

    def reset_game_mode(self):
        self.game_running = False
        # Unbind all keys
        self.parent_frame.unbind("<KeyPress>")
        self.parent_frame.unbind("<KeyRelease>")

        # Clear existing game elements
        if self.game_elements_created:
            self.canvas.delete("all")
            self.game_elements_created = False

        # Destroy existing buttons
        if hasattr(self, 'start_button') and self.start_button.winfo_exists():
            self.start_button.destroy()
        if hasattr(self, 'reset_mode_button') and self.reset_mode_button.winfo_exists():
            self.reset_mode_button.destroy()
        if hasattr(self, 'back_button') and self.back_button.winfo_exists():
            self.back_button.destroy()
            
        self.canvas.pack_forget() # Hide canvas
        self.mode_selection_frame.pack(pady=20) # Show mode selection again

    def reset_game(self):
        self.score_player1 = 0
        self.score_player2 = 0
        self.game_running = False
        if hasattr(self, 'start_button') and self.start_button.winfo_exists():
            self.start_button.config(state=tk.NORMAL, text="Iniciar Juego")
        self.reset_ball_position()


    def start_game(self):
        # Scores are reset in reset_game(), which is called before this in start_game_mode()
        self.canvas.itemconfig(self.score_display, text=f"{self.score_player1} - {self.score_player2}")
        self.ball_dx = self.initial_ball_speed
        self.ball_dy = self.initial_ball_speed
        self.game_running = True
        self.start_button.config(state=tk.DISABLED)
        self.reset_ball_position()
        self.game_loop()

    def go_to_main_menu(self):
        self.game_running = False
        # Unbind all keys
        self.parent_frame.unbind("<KeyPress>")
        self.parent_frame.unbind("<KeyRelease>")

        self.main_frame.destroy()
        self.show_main_menu_callback()

    def move_paddles(self):
        if self.player1_move != 0:
            self.canvas.move(self.player_paddle, 0, self.player1_move * self.paddle_speed)
            self.check_paddle_bounds(self.player_paddle)
        if self.game_mode == "PVP" and self.player2_move != 0:
            self.canvas.move(self.player2_paddle, 0, self.player2_move * self.paddle_speed)
            self.check_paddle_bounds(self.player2_paddle)

    def check_paddle_bounds(self, paddle):
        coords = self.canvas.coords(paddle)
        if coords and coords[1] < 0:
            self.canvas.coords(paddle, coords[0], 0, coords[2], 100)
        elif coords and coords[3] > 400:
            self.canvas.coords(paddle, coords[0], 300, coords[2], 400)

    def move_pc_paddle(self):
        paddle_coords = self.canvas.coords(self.pc_paddle_id)
        ball_coords = self.canvas.coords(self.ball)
        
        # Simple AI: PC paddle tries to follow the ball's y-position
        # Only move if the ball is on the PC's side and moving towards it
        if ball_coords[0] > 300 and self.ball_dx > 0:
            if ball_coords[1] < paddle_coords[1]:
                self.canvas.move(self.pc_paddle_id, 0, -self.paddle_speed * 0.7) # Move up
            elif ball_coords[3] > paddle_coords[3]:
                self.canvas.move(self.pc_paddle_id, 0, self.paddle_speed * 0.7) # Move down
        
        self.check_paddle_bounds(self.pc_paddle_id)

    def reset_ball_position(self):
        if self.ball: # Only reset if ball exists
            self.canvas.coords(self.ball, 290, 190, 310, 210)
        self.ball_dx = self.initial_ball_speed * random.choice([-1, 1])
        self.ball_dy = self.initial_ball_speed * random.choice([-1, 1])
        # Update score display after reset
        if self.score_display: # Only update if score_display exists
            self.canvas.itemconfig(self.score_display, text=f"{self.score_player1} - {self.score_player2}")

    def move_ball(self):
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        ball_coords = self.canvas.coords(self.ball)

        # Wall collision (top/bottom)
        if ball_coords[1] <= 0 or ball_coords[3] >= 400:
            self.ball_dy *= -1

        # Paddle collision (player_paddle)
        player_paddle_coords = self.canvas.coords(self.player_paddle)
        if (ball_coords[0] <= player_paddle_coords[2] and
                player_paddle_coords[0] <= ball_coords[2] and
                ball_coords[3] >= player_paddle_coords[1] and
                ball_coords[1] <= player_paddle_coords[3] and
                self.ball_dx < 0): # Ensure ball is moving towards the paddle
            self.ball_dx *= -1
            self.ball_dx += self.ball_speed_increment if self.ball_dx > 0 else -self.ball_speed_increment
            self.ball_dy += self.ball_speed_increment if self.ball_dy > 0 else -self.ball_speed_increment

        # Paddle collision (player2_paddle or pc_paddle_id)
        if self.game_mode == "PVP":
            right_paddle_coords = self.canvas.coords(self.player2_paddle)
        elif self.game_mode == "PVC":
            right_paddle_coords = self.canvas.coords(self.pc_paddle_id)
        else:
            right_paddle_coords = None

        if right_paddle_coords and (ball_coords[2] >= right_paddle_coords[0] and
                                    right_paddle_coords[2] >= ball_coords[0] and
                                    ball_coords[3] >= right_paddle_coords[1] and
                                    ball_coords[1] <= right_paddle_coords[3] and
                                    self.ball_dx > 0): # Ensure ball is moving towards the paddle
            self.ball_dx *= -1
            self.ball_dx += self.ball_speed_increment if self.ball_dx > 0 else -self.ball_speed_increment
            self.ball_dy += self.ball_speed_increment if self.ball_dy > 0 else -self.ball_speed_increment


        # Scoring
        if ball_coords[0] < 0:  # Player 2 (or PC) scores
            self.score_player2 += 1
            self.reset_ball_position()
            self.check_win()
        elif ball_coords[2] > 600:  # Player 1 scores
            self.score_player1 += 1
            self.reset_ball_position()
            self.check_win()

        if self.score_display:
            self.canvas.itemconfig(self.score_display, text=f"{self.score_player1} - {self.score_player2}")

    def check_win(self):
        if self.score_player1 >= self.max_score:
            self.show_winner("Jugador 1")
        elif self.score_player2 >= self.max_score:
            if self.game_mode == "PVC":
                self.show_winner("PC")
            else:
                self.show_winner("Jugador 2")

    def show_winner(self, winner_name):
        self.game_running = False
        messagebox.showinfo("Fin del Juego", f"¡{winner_name} ha ganado el juego!")
        self.reset_game_mode() # Go back to mode selection and reset everything





class MinesweeperGame:
    def __init__(self, parent_frame, show_main_menu_callback):
        self.parent_frame = parent_frame
        self.show_main_menu_callback = show_main_menu_callback
        
        self.main_frame = tk.Frame(parent_frame)
        self.main_frame.pack()

        self.difficulty_frame = tk.Frame(self.main_frame)
        self.difficulty_frame.pack(pady=20)
        
        tk.Label(self.difficulty_frame, text="Selecciona la dificultad:", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.difficulty_frame, text="Fácil (10x10, 10 minas)", command=lambda: self.start_game(10, 10, 10)).pack(pady=5)
        tk.Button(self.difficulty_frame, text="Medio (16x16, 40 minas)", command=lambda: self.start_game(16, 16, 40)).pack(pady=5)
        tk.Button(self.difficulty_frame, text="Difícil (30x16, 99 minas)", command=lambda: self.start_game(30, 16, 99)).pack(pady=5)
        tk.Button(self.difficulty_frame, text="Volver al Menú", command=self.show_main_menu_callback).pack(pady=20)
        
        self.game_frame = tk.Frame(self.main_frame)
        self.info_frame = tk.Frame(self.game_frame)
        self.board_frame = tk.Frame(self.game_frame)
        
    def start_game(self, width, height, mines):
        self.difficulty_frame.pack_forget()
        self.game_frame.pack()
        self.info_frame.pack(pady=5)
        self.board_frame.pack(pady=5)

        self.width = width
        self.height = height
        self.num_mines = mines
        self.flags_placed = 0
        self.game_over = False

        self.mines_label = tk.Label(self.info_frame, text=f"Minas: {self.num_mines - self.flags_placed}", font=("Arial", 12))
        self.mines_label.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(self.info_frame, text="Reiniciar", command=self.reset_game)
        self.reset_button.pack(side=tk.RIGHT, padx=10)
        
        self.back_to_menu_button = tk.Button(self.info_frame, text="Menú Principal", command=self.go_to_main_menu)
        self.back_to_menu_button.pack(side=tk.RIGHT, padx=10)

        self.create_board()

    def go_to_main_menu(self):
        self.main_frame.destroy()
        self.show_main_menu_callback()

    def create_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.buttons = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]

        for r in range(self.height):
            for c in range(self.width):
                btn = tk.Button(self.board_frame, text="", width=2, height=1, command=lambda r=r, c=c: self.on_left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.on_right_click(e, r, c))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn
        
        self.place_mines()

    def place_mines(self):
        mines_placed = 0
        while mines_placed < self.num_mines:
            r = random.randint(0, self.height - 1)
            c = random.randint(0, self.width - 1)
            if self.board[r][c] != -1:
                self.board[r][c] = -1 # -1 represents a mine
                mines_placed += 1
        
        # Calculate numbers
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] != -1:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if 0 <= r + dr < self.height and 0 <= c + dc < self.width and self.board[r + dr][c + dc] == -1:
                                count += 1
                    self.board[r][c] = count

    def on_left_click(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return

        self.revealed[r][c] = True
        self.buttons[r][c].config(state=tk.DISABLED, relief=tk.SUNKEN)

        if self.board[r][c] == -1:
            self.buttons[r][c].config(text="*", background="red")
            self.game_over = True
            messagebox.showerror("Buscaminas", "¡Has perdido!")
            self.reveal_all_mines()
        elif self.board[r][c] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if 0 <= r + dr < self.height and 0 <= c + dc < self.width:
                        self.on_left_click(r + dr, c + dc)
        else:
            self.buttons[r][c].config(text=str(self.board[r][c]))
        
        self.check_win()

    def on_right_click(self, event, r, c):
        if self.game_over or self.revealed[r][c]:
            return

        if self.buttons[r][c]["text"] == "":
            self.buttons[r][c].config(text="F", fg="red")
            self.flags_placed += 1
        elif self.buttons[r][c]["text"] == "F":
            self.buttons[r][c].config(text="?", fg="black")
            self.flags_placed -= 1
        elif self.buttons[r][c]["text"] == "?":
            self.buttons[r][c].config(text="")

        self.mines_label.config(text=f"Minas: {self.num_mines - self.flags_placed}")

    def check_win(self):
        revealed_count = 0
        for r in range(self.height):
            for c in range(self.width):
                if self.revealed[r][c]:
                    revealed_count += 1
        
        if revealed_count == self.width * self.height - self.num_mines:
            self.game_over = True
            messagebox.showinfo("Buscaminas", "¡Has ganado!")
            self.reveal_all_mines()

    def reveal_all_mines(self):
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] == -1:
                    self.buttons[r][c].config(text="*", background="red")
    
    def reset_game(self):
        self.game_over = False
        self.flags_placed = 0
        self.mines_label.config(text=f"Minas: {self.num_mines - self.flags_placed}")
        self.create_board()


class TrikiGame:
    """
    Clase que encapsula toda la lógica y la interfaz del juego 'Triki a la 2'.
    """
    def __init__(self, parent_frame, show_main_menu_callback):
        self.parent_frame = parent_frame
        self.show_main_menu_callback = show_main_menu_callback
        
        # Variables del juego
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.scores = {"X": 0, "O": 0}
        self.game_over = False
        self.time_left = 60
        self.timer_id = None
        self.game_mode = None # "PVP" o "PVC"

        # --- Interfaz Gráfica ---
        self.main_frame = tk.Frame(parent_frame)
        self.main_frame.pack()

        # Frame para la selección de modo
        self.mode_selection_frame = tk.Frame(self.main_frame)
        self.mode_selection_frame.pack(pady=20)
        
        mode_label = tk.Label(self.mode_selection_frame, text="Selecciona un modo de juego:", font=("Arial", 16))
        mode_label.pack(pady=10)

        pvp_button = tk.Button(self.mode_selection_frame, text="Jugador vs Jugador", font=("Arial", 14), command=lambda: self.start_game_mode("PVP"))
        pvp_button.pack(pady=5)

        pvc_button = tk.Button(self.mode_selection_frame, text="Jugador vs PC", font=("Arial", 14), command=lambda: self.start_game_mode("PVC"))
        pvc_button.pack(pady=5)
        
        back_button = tk.Button(self.mode_selection_frame, text="Volver al Menú Principal", font=("Arial", 10), command=self.show_main_menu_callback)
        back_button.pack(pady=20)


        # Frame para el tablero (inicialmente oculto)
        self.board_frame = tk.Frame(self.main_frame)

        # Matriz de botones para el tablero
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(
                    self.board_frame,
                    text="",
                    font=("Arial", 24, "bold"),
                    width=5,
                    height=2,
                    command=lambda i=i, j=j: self.on_button_click(i, j),
                )
                self.buttons[i][j].grid(row=i, column=j)

        # Frame para información (inicialmente oculto)
        self.info_frame = tk.Frame(self.main_frame)

        # Etiqueta para el turno del jugador
        self.turn_label = tk.Label(
            self.info_frame, text="", font=("Arial", 14)
        )
        self.turn_label.pack()

        # Etiqueta para los puntajes
        self.score_label = tk.Label(
            self.info_frame, text="", font=("Arial", 14)
        )
        self.score_label.pack()

        # Etiqueta para el temporizador
        self.timer_label = tk.Label(
            self.info_frame, text=f"Tiempo restante: {self.time_left}s", font=("Arial", 14)
        )
        self.timer_label.pack()

        # Botón para reiniciar el juego completo (inicialmente oculto)
        self.restart_button = tk.Button(
            self.main_frame, text="Cambiar de Modo", command=self.reset_game
        )
        
        self.back_to_menu_button = tk.Button(
            self.main_frame, text="Volver al Menú Principal", command=self.go_to_main_menu
        )


    def start_game_mode(self, mode):
        self.game_mode = mode
        self.mode_selection_frame.pack_forget()
        
        # Mostrar los frames del juego
        self.board_frame.pack(pady=10)
        self.info_frame.pack(pady=10)
        self.restart_button.pack(pady=10)
        self.back_to_menu_button.pack(pady=5)
        
        self.update_score_label()
        self.start_new_round()

    def go_to_main_menu(self):
        self.stop_timer()
        self.show_main_menu_callback()

    def on_button_click(self, i, j):
        if self.board[i][j] == "" and not self.game_over:
            if self.game_mode == "PVC" and self.current_player == "O":
                return 
            self.make_move(i, j)

    def make_move(self, i, j):
        self.board[i][j] = self.current_player
        self.buttons[i][j].config(
            text=self.current_player,
            fg="red" if self.current_player == "X" else "blue",
            disabledforeground="red" if self.current_player == "X" else "blue",
            state="disabled"
        )
        self.reset_timer()

        if self.check_winner(self.current_player):
            self.handle_round_winner()
        elif all(self.board[row][col] != "" for row in range(3) for col in range(3)):
            self.game_over = True
            messagebox.showinfo("Fin de la Partida", "¡Es un empate!")
            self.start_new_round()
        else:
            self.switch_player()
            self.start_timer()

    def pc_move(self):
        if self.game_over:
            return
        
        # AI Logic... (same as before)
        # 1. Intentar ganar
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    if self.check_winner("O"):
                        self.make_move(i, j)
                        return
                    self.board[i][j] = ""

        # 2. Bloquear al jugador
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "X"
                    if self.check_winner("X"):
                        self.board[i][j] = ""
                        self.make_move(i, j)
                        return
                    self.board[i][j] = ""

        # 3. Tomar el centro
        if self.board[1][1] == "":
            self.make_move(1, 1)
            return

        # 4. Tomar una esquina vacía
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        random.shuffle(corners)
        for i, j in corners:
            if self.board[i][j] == "":
                self.make_move(i, j)
                return

        # 5. Tomar un lado vacío
        sides = [(0, 1), (1, 0), (1, 2), (2, 1)]
        random.shuffle(sides)
        for i, j in sides:
            if self.board[i][j] == "":
                self.make_move(i, j)
                return

    def handle_round_winner(self):
        self.game_over = True
        self.stop_timer()
        self.scores[self.current_player] += 1
        self.update_score_label()

        winner_name = self.get_player_name(self.current_player)
        if self.scores[self.current_player] == 5:
            self.show_victory()
        else:
            messagebox.showinfo("Fin de la Ronda", f"¡{winner_name} ha ganado la ronda!")
            self.start_new_round()

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_turn_label()
        
        if self.game_mode == "PVC" and self.current_player == "O" and not self.game_over:
            self.parent_frame.after(500, self.pc_move)

    def check_winner(self, player):
        # ... (same as before)
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)): return True
        for j in range(3):
            if all(self.board[i][j] == player for i in range(3)): return True
        if all(self.board[i][i] == player for i in range(3)): return True
        if all(self.board[i][2 - i] == player for i in range(3)): return True
        return False

    def update_score_label(self):
        if self.game_mode == "PVC":
            self.score_label.config(text=f"Puntajes: Jugador: {self.scores['X']} - PC: {self.scores['O']}")
        else:
            self.score_label.config(text=f"Puntajes: Jugador X: {self.scores['X']} - Jugador O: {self.scores['O']}")
            
    def update_turn_label(self):
        player_name = self.get_player_name(self.current_player)
        self.turn_label.config(text=f"Turno de: {player_name}")

    def start_new_round(self):
        self.game_over = False
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state="normal")

        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_turn_label()
        self.reset_timer()
        self.start_timer()
        
        if self.game_mode == "PVC" and self.current_player == "O":
            self.parent_frame.after(500, self.pc_move)

    def reset_game(self):
        self.stop_timer()
        self.scores = {"X": 0, "O": 0}
        
        # Destruir widgets del juego y mostrar el menú de modo
        self.board_frame.pack_forget()
        self.info_frame.pack_forget()
        self.restart_button.pack_forget()
        self.back_to_menu_button.pack_forget()
        
        self.mode_selection_frame.pack(pady=20)


    def start_timer(self):
        if self.game_over: return
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Tiempo restante: {self.time_left}s")
            self.timer_id = self.parent_frame.after(1000, self.start_timer)
        else:
            self.handle_timeout()

    def stop_timer(self):
        if self.timer_id:
            self.parent_frame.after_cancel(self.timer_id)
            self.timer_id = None

    def reset_timer(self):
        self.stop_timer()
        self.time_left = 60
        self.timer_label.config(text=f"Tiempo restante: {self.time_left}s")

    def handle_timeout(self):
        # ... (same as before)
        self.game_over = True
        loser = self.current_player
        winner = "O" if loser == "X" else "X"
        loser_name = self.get_player_name(loser)
        winner_name = self.get_player_name(winner)
        messagebox.showwarning("¡Tiempo Agotado!", f"{loser_name} no hizo un movimiento a tiempo.\n¡{winner_name} gana un punto!")
        self.scores[winner] += 1
        self.update_score_label()
        if self.scores[winner] == 5: self.show_victory()
        else: self.start_new_round()
            
    def get_player_name(self, player_symbol):
        if self.game_mode == "PVC":
            return "Jugador" if player_symbol == "X" else "PC"
        else:
            return f"Jugador {player_symbol}"

    def show_victory(self):
        # ... (same as before)
        winner = "X" if self.scores["X"] == 5 else "O"
        winner_name = self.get_player_name(winner)
        
        # Use Toplevel on the root window
        victory_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
        victory_window.title("¡VICTORIA!")
        victory_window.geometry("300x300")
        
        # ... rest of the victory window code is the same ...
        victory_label = tk.Label(victory_window, text=f"¡VICTORIA PARA {winner_name.upper()}!", font=("Arial", 16, "bold"))
        victory_label.pack(pady=10)
        cat_ascii = r"""
          /\_/\
         ( o.o )
          > ^ <
        """
        cat_label = tk.Label(victory_window, text=cat_ascii, font=("Courier", 14), justify=tk.CENTER)
        cat_label.pack()
        close_button = tk.Button(victory_window, text="Jugar de Nuevo", command=lambda: [victory_window.destroy(), self.reset_game()])
        close_button.pack(pady=5)
        exit_button = tk.Button(victory_window, text="Salir", command=self.parent_frame.winfo_toplevel().destroy)
        exit_button.pack(pady=5)
        victory_window.protocol("WM_DELETE_WINDOW", self.parent_frame.winfo_toplevel().destroy)
        self.parent_frame.winfo_toplevel().withdraw()
        def on_victory_close(): self.parent_frame.winfo_toplevel().destroy()
        victory_window.protocol("WM_DELETE_WINDOW", on_victory_close)

if __name__ == "__main__":
    main_root = tk.Tk()
    app = MainApp(main_root)
    main_root.mainloop()
