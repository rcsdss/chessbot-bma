import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from tkinter import PhotoImage, ttk
import chess
import chess.engine
from PIL import Image, ImageTk
import os
import time

VERSION = "chessbot v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Willkommen zu dem BR Bot Retry")
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="black")
        self.board = chess.Board()
        # Set relative path use os.path
        self.engine_path = os.path.join(os.getcwd(), "stockfish", "stockfish-windows-x86-64-avx2.exe")
        if not os.path.exists(self.engine_path):
            self.engine_path = self.browse_for_engine()  # Prompt user to select the engine path
            if not self.engine_path:
                messagebox.showerror("Fehler", "Kein Pfad zur Engine ausgewählt. Das Programm wird beendet.")
                root.quit()
            else:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        else:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.squares = {}
        self.selected_piece = None
        self.captured_pieces_player = []
        self.captured_pieces_bot = []
        self.piece_values = {
            'p': 1, 'r': 5, 'n': 3, 'b': 3, 'q': 9, 'k': 0,
            'P': 1, 'R': 5, 'N': 3, 'B': 3, 'Q': 9, 'K': 0
        }
        self.undo_stack = []  # Stack for undo moves
        self.game_started = False  # Track if the game has started
        self.player_name = "Spieler 1"
        self.bot_name = "Bot"
        self.player_country = "ch"  # Default country is Switzerland
        self.bot_country = "ch"  # Default to Switzerland for bot as well
        self.player_elo = 800
        self.bot_elo = 1200
        self.player_time = None  # Player timer setting
        self.bot_time = None  # Bot timer setting
        self.player_increment = 0  # Player increment per move
        self.bot_increment = 0  # Bot increment per move
        self.create_main_menu()

    def browse_for_engine(self):
        # Function to prompt user to browse for the Stockfish engine
        engine_path = filedialog.askopenfilename(title="Select Stockfish Engine", filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
        return engine_path

    def create_main_menu(self):
        # Create the main menu interface
        self.clear_screen()

        self.general_frame = tk.Frame(self.root, bg="black")
        self.general_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)

        # Configure a 3x2 grid layout that takes the entire screen
        self.general_frame.grid_rowconfigure(0, weight=1)
        self.general_frame.grid_rowconfigure(1, weight=8)
        self.general_frame.grid_rowconfigure(2, weight=1)
        self.general_frame.grid_columnconfigure(0, weight=1)
        self.general_frame.grid_columnconfigure(1, weight=1)

        # Add title at the top
        self.title_frame = tk.Frame(self.general_frame, bg="black")
        self.title_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.title_label = tk.Label(self.title_frame, text="Willkommen zu dem BR Bot Retry", font=("Arial", 40), fg="white", bg="black")
        self.title_label.pack(anchor="center")

        # Top left: Robot with difficulty levels
        self.top_left_frame = tk.Frame(self.general_frame, bg="black", highlightthickness=0)
        self.top_left_frame.grid(row=1, column=0, sticky="nsew")

        # Robot emoji
        self.robot_label = tk.Label(self.top_left_frame, text="🤖", font=("Arial", 200), bg="black", fg="white")
        self.robot_label.pack(anchor="center")

        # Difficulty level buttons
        button_width = 20
        button_height = 2
        self.easy_button = tk.Button(self.top_left_frame, text="Easy 😊", font=("Arial", 20), bg="black", fg="white", command=lambda: self.start_game("easy"), width=button_width, height=button_height, relief=tk.FLAT)
        self.easy_button.pack(anchor="center", pady=(10, 5))

        self.medium_button = tk.Button(self.top_left_frame, text="Medium 😎", font=("Arial", 20), bg="black", fg="white", command=lambda: self.start_game("medium"), width=button_width, height=button_height, relief=tk.FLAT)
        self.medium_button.pack(anchor="center", pady=5)

        self.hard_button = tk.Button(self.top_left_frame, text="Hard 🤓", font=("Arial", 20), bg="black", fg="white", command=lambda: self.start_game("hard"), width=button_width, height=button_height, relief=tk.FLAT)
        self.hard_button.pack(anchor="center", pady=5)

        # Top right: Play against a friend
        self.top_right_frame = tk.Frame(self.general_frame, bg="black", highlightthickness=0)
        self.top_right_frame.grid(row=1, column=1, sticky="nsew")

        self.friend_button = tk.Button(self.top_right_frame, text="👥", font=("Arial", 200), bg="black", fg="white", command=self.start_friend_game, relief=tk.FLAT)
        self.friend_button.pack(anchor="center")

        # Bottom left: Quit button
        self.bottom_left_frame = tk.Frame(self.general_frame, bg="black", highlightthickness=0)
        self.bottom_left_frame.grid(row=2, column=0, sticky="nsew")

        self.quit_button = tk.Button(self.bottom_left_frame, text="Quit ❌", font=("Arial", 80), bg="black", fg="red", command=self.on_closing, relief=tk.FLAT)
        self.quit_button.pack(anchor="center")

        # Bottom right: BMA button leading to rules and documentation
        self.bottom_right_frame = tk.Frame(self.general_frame, bg="black", highlightthickness=0)
        self.bottom_right_frame.grid(row=2, column=1, sticky="nsew")

        self.bma_button = tk.Button(self.bottom_right_frame, text="BMA", font=("Arial", 80), bg="gray", fg="white", command=self.show_bma_options, relief=tk.FLAT)
        self.bma_button.pack(anchor="center")

    def show_bma_options(self):
        # Show options for rules and documentation
        messagebox.showinfo("BMA", "BMA Options: Spieleregeln und Dokumentation.")

    def create_game_interface(self):
        # Create the in-game interface with side menu
        self.clear_screen()
        self.general_frame = tk.Frame(self.root, bg="black")
        self.general_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Configure grid layout for the general frame
        self.general_frame.grid_rowconfigure(0, weight=1)
        self.general_frame.grid_rowconfigure(1, weight=8)
        self.general_frame.grid_rowconfigure(2, weight=1)
        self.general_frame.grid_columnconfigure(0, weight=1)
        self.general_frame.grid_columnconfigure(1, weight=8)
        self.general_frame.grid_columnconfigure(2, weight=1)

        # Top information frame for player and bot details
        self.top_info_frame = tk.Frame(self.general_frame, bg="black")
        self.top_info_frame.grid(row=0, column=1, sticky="nsew")

        # Bot piece bank (placed behind bot info)
        self.bot_bank_frame = tk.Frame(self.top_info_frame, bg="black")
        self.bot_bank_frame.place(x=110, y=50)  # Adjust x, y values for exact positioning
        self.bot_bank_canvas = tk.Canvas(self.bot_bank_frame, width=400, height=50, bg="black", highlightthickness=0)
        self.bot_bank_canvas.pack()

        # Bot information (top) - Placed after the bot bank to visually appear on top
        self.bot_photo_label = tk.Label(self.top_info_frame, text="🤖", font=("Arial", 50), bg="black", fg="white")
        self.bot_photo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.bot_name_label = tk.Label(self.top_info_frame, text=f"{self.bot_name} ({self.bot_elo})", font=("Arial", 16), fg="white", bg="black")
        self.bot_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.bot_flag_label = tk.Label(self.top_info_frame, text="🇨🇭", font=("Arial", 16), bg="black", fg="white")
        self.bot_flag_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.bot_clock_button = tk.Button(self.top_info_frame, text="⏲️", font=("Arial", 16), fg="yellow", bg="black", command=lambda: self.set_timer('bot'))
        self.bot_clock_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # Player information (bottom) - Placed after the player bank to visually appear on top
        self.bottom_info_frame = tk.Frame(self.general_frame, bg="black")
        self.bottom_info_frame.grid(row=2, column=1, sticky="nsew")

        # Player piece bank (placed behind player info)
        self.player_bank_frame = tk.Frame(self.bottom_info_frame, bg="black")
        self.player_bank_frame.place(x=110, y=50)  # Adjust x, y values for exact positioning
        self.player_bank_canvas = tk.Canvas(self.player_bank_frame, width=400, height=50, bg="black", highlightthickness=0)
        self.player_bank_canvas.pack()

        self.player_photo_label = tk.Label(self.bottom_info_frame, text="👤", font=("Arial", 50), bg="black", fg="white")
        self.player_photo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.player_name_label = tk.Label(self.bottom_info_frame, text=f"{self.player_name} ({self.player_elo})", font=("Arial", 16), fg="white", bg="black")
        self.player_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.player_flag_label = tk.Label(self.bottom_info_frame, text="🇨🇭", font=("Arial", 16), bg="black", fg="white")
        self.player_flag_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.player_clock_button = tk.Button(self.bottom_info_frame, text="⏲️", font=("Arial", 16), fg="yellow", bg="black", command=lambda: self.set_timer('player'))
        self.player_clock_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # Create the left menu with buttons for game controls
        self.menu_frame = tk.Frame(self.general_frame, bg="black")
        self.menu_frame.grid(row=1, column=0, sticky="ns")

        self.param_button = tk.Button(self.menu_frame, text="Paramètres", font=("Arial", 16), command=self.show_parameters, bg="gray", fg="white")
        self.param_button.pack(pady=5, fill=tk.X)

        self.undo_button = tk.Button(self.menu_frame, text="Zug rückgängig machen", font=("Arial", 16), command=self.undo_move, bg="gray", fg="white")
        self.undo_button.pack(pady=5, fill=tk.X)

        self.abandon_button = tk.Button(self.menu_frame, text="Abandonner / Annuler", font=("Arial", 16), command=self.abandon_game, bg="gray", fg="red")
        self.abandon_button.pack(pady=5, fill=tk.X)

        self.home_button = tk.Button(self.menu_frame, text="Retour à l'accueil", font=("Arial", 16), command=self.create_main_menu, bg="gray", fg="white")
        self.home_button.pack(pady=5, fill=tk.X)

        self.analyze_button = tk.Button(self.menu_frame, text="Analyse", font=("Arial", 16), command=self.analyze_game, bg="gray", fg="white")
        self.analyze_button.pack(pady=5, fill=tk.X)

        # Frame for the chessboard
        self.board_frame = tk.Frame(self.general_frame, bg="black")
        self.board_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Create chessboard
        self.square_size = 100  # Adjust size accordingly
        for row in range(8):
            for col in range(8):
                square = tk.Canvas(self.board_frame, width=self.square_size, height=self.square_size, highlightthickness=0)
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.handle_square_click(r, c))
                self.squares[(row, col)] = square

        # Frame for move history or bot output
        self.output_frame = tk.Frame(self.general_frame, bg="black")
        self.output_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.output_frame, width=30, height=40, font=("Arial", 12), bg="black", fg="white", wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Willkommen beim Schachbot! Weiß ist am Zug\n")
        self.output_text.configure(state='disabled')  # Disable writing
        self.update_board()

    def start_game(self, difficulty):
        # Function to start a game with selected difficulty
        self.create_game_interface()
        # Additional setup for game difficulty
        if difficulty == "easy":
            self.bot_time_limit = 0.2
            self.bot_depth = 5
        elif difficulty == "medium":
            self.bot_time_limit = 0.5
            self.bot_depth = 10
        elif difficulty == "hard":
            self.bot_time_limit = 1.0
            self.bot_depth = 20
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, f"Starting game with {difficulty} difficulty.\n")
        self.output_text.configure(state='disabled')
        self.game_started = True
        self.start_timers()  # Start timers when the game starts

    def start_friend_game(self):
        # Function to start a game against a friend
        self.create_game_interface()
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, "Starting game against a friend.\n")
        self.output_text.configure(state='disabled')
        self.game_started = True
        self.start_timers()  # Start timers when the game starts

    def abandon_game(self):
        # Function to abandon or cancel a game
        self.game_started = False
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, "You have abandoned the game.\n")
        self.output_text.configure(state='disabled')
        self.create_main_menu()

    def show_parameters(self):
        # Show parameter options (e.g., change name, time settings)
        messagebox.showinfo("Paramètres", "Parameter settings here.")

    def undo_move(self):
        # Function to undo a move
        if self.undo_stack:
            self.board = self.undo_stack.pop()
            self.update_board()
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "Zug rückgängig gemacht\n")
            self.output_text.configure(state='disabled')
        else:
            messagebox.showinfo("Keine Züge", "Es gibt keine Züge zum Rückgängigmachen.")

    def analyze_game(self):
        # Function for analyzing the current game (to be implemented)
        messagebox.showinfo("Analyse", "Game analysis is not yet implemented.")

    def handle_square_click(self, row, col):
        # Handle click event for each square, either player or bot move
        if not self.game_started:
            return  # Prevent moves before pressing play button
        selected_square = chess.square(col, 7 - row)
        if self.selected_piece is not None:
            move = chess.Move(self.selected_piece, selected_square)
            if move in self.board.legal_moves:
                self.undo_stack.append(self.board.copy())  # Add current board state to stack
                if self.board.is_capture(move):
                    captured_piece = self.board.piece_at(move.to_square)
                    self.captured_pieces_player.append(captured_piece.symbol())
                self.board.push(move)
                self.selected_piece = None
                self.update_board()
                self.output_text.configure(state='normal')
                self.output_text.insert(tk.END, f"Move: {move.uci()}\n")
                self.output_text.configure(state='disabled')
                if self.board.is_check():
                    king_square = self.board.king(self.board.turn)
                    row, col = divmod(king_square, 8)
                    self.squares[(7 - row, col)].create_rectangle(0, 0, self.square_size, self.square_size, outline="red", width=5)
                if not self.board.turn:
                    self.bot_move()
            else:
                self.selected_piece = None  # Deselect if move is not legal
                self.update_board()  # Remove any highlighted moves
        else:
            piece = self.board.piece_at(selected_square)
            if piece and piece.color == self.board.turn:
                self.selected_piece = selected_square
                self.highlight_moves(selected_square)

    def bot_move(self):
        # Bot makes a move
        result = self.engine.play(self.board, chess.engine.Limit(time=self.bot_time_limit))
        if self.board.is_capture(result.move):
            captured_piece = self.board.piece_at(result.move.to_square)
            self.captured_pieces_bot.append(captured_piece.symbol())
        self.board.push(result.move)
        self.update_board()
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, f"Bot: {result.move.uci()}\n")
        self.output_text.configure(state='disabled')
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            row, col = divmod(king_square, 8)
            self.squares[(7 - row, col)].create_rectangle(0, 0, self.square_size, self.square_size, outline="red", width=5)

    def highlight_moves(self, square):
        # Highlight possible moves for the selected piece with a filled oval
        moves = list(self.board.legal_moves)
        for move in moves:
            if move.from_square == square:
                row, col = divmod(move.to_square, 8)
                self.squares[(7 - row, col)].create_oval(35, 35, self.square_size - 35, self.square_size - 35, fill="green", outline="")

    def update_board(self):
        # Update the chessboard's visual representation
        self.pieces = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        for row in range(8):
            for col in range(8):
                square = self.squares[(row, col)]
                square.delete("all")
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                square.create_rectangle(0, 0, self.square_size, self.square_size, outline="black", fill=color)
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    symbol = self.pieces[piece.symbol()]
                    square.create_text(self.square_size // 2, self.square_size // 2, text=symbol, font=("Arial", int(self.square_size * 0.5)), anchor="center")
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            row, col = divmod(king_square, 8)
            self.squares[(7 - row, col)].create_rectangle(0, 0, self.square_size, self.square_size, outline="red", width=5)

        # Update piece banks
        self.update_piece_banks()

    def update_piece_banks(self):
        # Update piece banks for both player and bot
        self.bot_bank_canvas.delete("all")
        self.player_bank_canvas.delete("all")

        piece_x_offset = 10
        for idx, piece_symbol in enumerate(self.captured_pieces_bot):
            self.bot_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")
        for idx, piece_symbol in enumerate(self.captured_pieces_player):
            self.player_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")

        # Update the advantage indicator
        self.update_advantage()

    def update_advantage(self):
        # Update advantage calculation at the end of the piece bank
        player_advantage = sum(self.piece_values[piece] for piece in self.captured_pieces_bot)
        bot_advantage = sum(self.piece_values[piece] for piece in self.captured_pieces_player)

        advantage = player_advantage - bot_advantage

        if advantage > 0:
            advantage_text = f"+{advantage}"
            self.player_bank_canvas.create_text(360, 25, text=advantage_text, font=("Arial", 16), fill="red")  # Shifted position to the right for better spacing
        elif advantage < 0:
            advantage_text = f"+{-advantage}"
            self.bot_bank_canvas.create_text(360, 25, text=advantage_text, font=("Arial", 16), fill="red")  # Shifted position to the right for better spacing

    def clear_screen(self):
        # Clear the current screen
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_closing(self):
        # Handle the closing event
        if hasattr(self, 'engine') and self.engine:
            self.engine.quit()
        self.root.destroy()
        messagebox.showinfo("Auf Wiedersehen", "Das Programm wird jetzt beendet.")

    def set_timer(self, player_type):
        # Set the timer for the player or bot
        timer_window = tk.Toplevel(self.root)
        timer_window.title("Set Timer")
        timer_window.configure(bg="black")

        options = [
            ("Bullet", ["1 min", "1 | 1", "2 | 1"]),
            ("Blitz", ["3 min", "3 | 2", "5 min"]),
            ("Mode Rapide", ["10 min", "15 | 10", "30 min"]),
            ("No Time", [])
        ]

        for category, times in options:
            category_label = tk.Label(timer_window, text=category, font=("Arial", 16), fg="white", bg="black")
            category_label.pack(anchor="w", padx=10, pady=5)
            for time in times:
                timer_button = tk.Button(timer_window, text=time, font=("Arial", 14), bg="gray", fg="black", command=lambda t=time, p=player_type: self.set_time_for_player(p, t))
                timer_button.pack(anchor="w", padx=20, pady=2)
            if category == "No Time":
                timer_button = tk.Button(timer_window, text="No Time", font=("Arial", 14), bg="gray", fg="black", command=lambda t="No Time", p=player_type: self.set_time_for_player(p, t))
                timer_button.pack(anchor="w", padx=20, pady=2)

    def set_time_for_player(self, player_type, time):
        # Set the selected time for the player or bot
        increment = 0
        if "|" in time:
            base_time, increment = time.split("|")
            increment = int(increment.strip())
            base_time = base_time.strip()
        else:
            base_time = time.strip()

        if base_time.endswith("min"):
            minutes = int(base_time.replace("min", "").strip())
            seconds = minutes * 60
        elif base_time.endswith("sec"):
            seconds = int(base_time.replace("sec", "").strip())
        else:
            seconds = None

        if player_type == 'player':
            self.player_time = seconds
            self.player_increment = increment
            self.player_clock_button.config(text=f"⏲️ {time}")
        elif player_type == 'bot':
            self.bot_time = seconds
            self.bot_increment = increment
            self.bot_clock_button.config(text=f"⏲️ {time}")

    def start_timers(self):
        if self.player_time is not None and self.bot_time is not None:
            self.player_time_left = self.player_time
            self.bot_time_left = self.bot_time
            self.update_timer_display('player')
            self.update_timer_display('bot')
            if self.board.turn == chess.WHITE:
                self.start_player_timer()
            else:
                self.start_bot_timer()

    def start_player_timer(self):
        if self.player_time_left > 0 and self.board.turn == chess.WHITE and self.game_started:
            self.player_time_left -= 1
            self.update_timer_display('player')
            self.root.after(1000, self.start_player_timer)
        elif self.player_time_left == 0:
            messagebox.showinfo("Time's Up!", "Player 1's time is up!")
            self.game_started = False

    def start_bot_timer(self):
        if self.bot_time_left > 0 and self.board.turn == chess.BLACK and self.game_started:
            self.bot_time_left -= 1
            self.update_timer_display('bot')
            self.root.after(1000, self.start_bot_timer)
        elif self.bot_time_left == 0:
            messagebox.showinfo("Time's Up!", "Bot's time is up!")
            self.game_started = False

    def update_timer_display(self, player_type):
        if player_type == 'player':
            minutes, seconds = divmod(self.player_time_left, 60)
            self.player_clock_button.config(text=f"⏲️ {minutes:02d}:{seconds:02d}")
        elif player_type == 'bot':
            minutes, seconds = divmod(self.bot_time_left, 60)
            self.bot_clock_button.config(text=f"⏲️ {minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    # Main program: Initialize and start the GUI
    root = tk.Tk()
    app = ChessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
