# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 22:34:54 2024

@author: Robin Corbonnois
"""

import tkinter as tk
from tkinter import messagebox
import chess
import chess.pgn
from io import StringIO

# Define the path to your Stockfish engine
STOCKFISH_PATH = r"C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\code\stockfish\stockfish-windows-x86-64-avx2.exe"

# Unicode symbols for chess pieces
PIECE_SYMBOLS = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
}

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game with FEN/PGN Input, Advantage Bar, Move Navigation")

        # Default mode to play
        self.mode = "play"
        self.selected_piece = None  # No piece selected initially

        # Set up board
        self.board = chess.Board()
        self.flipped = False
        self.selected_square = None
        self.move_history = []  # Keeps track of the moves (PGN history)
        self.current_move_index = 0  # Tracks the current position in the move history
        self.game = None  # Holds the PGN game object
        self.playing = False  # Keeps track of whether auto-play is active

        # Create canvas for the chessboard display
        self.canvas = tk.Canvas(self.root, width=450, height=450)  # Adjusted size for labels
        self.canvas.grid(row=0, column=0, padx=10)
        self.canvas.bind("<Button-1>", self.on_square_click)

        # Frame for controls and piece selection
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.grid(row=0, column=1, sticky="n")

        # Advantage Bar toggle and canvas
        self.advantage_bar_enabled = tk.BooleanVar()
        self.advantage_bar_checkbox = tk.Checkbutton(self.controls_frame, text="Show Advantage Bar",
                                                     variable=self.advantage_bar_enabled, command=self.update_board)
        self.advantage_bar_checkbox.grid(row=14, column=0, pady=5)

        self.advantage_bar_canvas = tk.Canvas(self.root, width=50, height=400, bg="gray")
        self.advantage_bar_canvas.grid(row=0, column=2)

        # Label to display the advantage as a number
        self.advantage_label = tk.Label(self.controls_frame, text="Advantage: N/A", font=("Helvetica", 12))
        self.advantage_label.grid(row=15, column=0, pady=10)

        # Button bar layout: Go to First Move, Previous Move, Play/Pause, Next Move, Go to Last Move
        button_bar = tk.Frame(self.controls_frame)
        button_bar.grid(row=16, column=0, pady=10)

        self.first_move_button = tk.Button(button_bar, text="⏮️", command=self.go_to_first_move, width=5)
        self.first_move_button.grid(row=0, column=0, padx=5)

        self.prev_move_button = tk.Button(button_bar, text="⏪", command=self.previous_move, width=5)
        self.prev_move_button.grid(row=0, column=1, padx=5)

        self.play_pause_button = tk.Button(button_bar, text="▶️", command=self.toggle_play_pause, width=5)
        self.play_pause_button.grid(row=0, column=2, padx=5)

        self.next_move_button = tk.Button(button_bar, text="⏩", command=self.next_move, width=5)
        self.next_move_button.grid(row=0, column=3, padx=5)

        self.last_move_button = tk.Button(button_bar, text="⏭️", command=self.go_to_last_move, width=5)
        self.last_move_button.grid(row=0, column=4, padx=5)

        # Button to toggle Edit Mode
        self.edit_mode_button = tk.Button(self.controls_frame, text="Switch to Edit Mode", command=self.toggle_mode)
        self.edit_mode_button.grid(row=18, column=0, pady=5)

        # Add piece selection and FEN/PGN display buttons
        self.create_piece_selection()

        # Input for FEN or PGN
        self.input_entry = tk.Entry(self.controls_frame, width=40)
        self.input_entry.grid(row=6, column=0, pady=10)
        self.input_entry.insert(0, "Enter FEN or PGN here")

        # Button to load FEN or PGN
        self.load_input_button = tk.Button(self.controls_frame, text="Load FEN/PGN", command=self.load_fen_or_pgn)
        self.load_input_button.grid(row=7, column=0, pady=5)

        # Button to clear a piece
        self.clear_button = tk.Button(self.controls_frame, text="Clear Piece", command=self.clear_piece, state=tk.DISABLED)
        self.clear_button.grid(row=8, column=0, pady=5)

        # Button to reset board to default starting position
        self.reset_button = tk.Button(self.controls_frame, text="Reset Board", command=self.reset_board, state=tk.DISABLED)
        self.reset_button.grid(row=9, column=0, pady=5)

        # Button to clear the entire board
        self.clear_board_button = tk.Button(self.controls_frame, text="Clear Board", command=self.clear_board, state=tk.DISABLED)
        self.clear_board_button.grid(row=10, column=0, pady=5)

        # White Turn / Black Turn indicator
        self.turn_label = tk.Label(self.controls_frame, text="White Turn", font=("Helvetica", 12), bg="white", width=20)
        self.turn_label.grid(row=11, column=0, pady=5)

        # Flip Board button
        self.flip_button = tk.Button(self.controls_frame, text="Flip Board", command=self.flip_board)
        self.flip_button.grid(row=12, column=0, pady=5)

        # Initialize the chessboard
        self.update_board()

    def create_piece_selection(self):
        """Creates a table-like layout of buttons to select chess pieces."""
        table_frame = tk.LabelFrame(self.controls_frame, text="Select Piece", padx=5, pady=5)
        table_frame.grid(row=2, column=0, padx=5, pady=5)

        pieces = ['R', 'N', 'B', 'Q', 'K', 'P', 'r', 'n', 'b', 'q', 'k', 'p']  # Uppercase for white, lowercase for black

        for idx, piece in enumerate(pieces):
            button_text = PIECE_SYMBOLS[piece]
            button = tk.Button(table_frame, text=button_text, width=6, font=("Arial", 20),
                               command=lambda p=piece: self.select_piece(p))
            row = (idx // 6)
            column = idx % 6
            button.grid(row=row, column=column, padx=4, pady=4)

    def select_piece(self, piece):
        """Sets the selected piece for placement and enters 'edit mode'."""
        self.selected_piece = piece

    def toggle_mode(self):
        """Toggle between play and edit modes."""
        if self.mode == "play":
            self.mode = "edit"
            self.edit_mode_button.config(text="Switch to Play Mode")
            self.enable_edit_buttons()
        else:
            self.mode = "play"
            self.edit_mode_button.config(text="Switch to Edit Mode")
            self.selected_piece = None  # Reset selected piece in play mode
            self.disable_edit_buttons()

    def enable_edit_buttons(self):
        """Enables the buttons related to editing the board."""
        self.clear_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_board_button.config(state=tk.NORMAL)

    def disable_edit_buttons(self):
        """Disables the buttons related to editing the board."""
        self.clear_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_board_button.config(state=tk.DISABLED)

    def clear_piece(self):
        """Enters 'clear mode' by deselecting any piece and allowing the user to clear pieces."""
        self.mode = "clear"
        self.selected_piece = None

    def on_square_click(self, event):
        """Handles when a square on the chessboard is clicked for piece movement, placing, or clearing."""
        square_size = 50
        file = (event.x - 25) // square_size  # Adjusted for the 25px margin for labels
        rank = 7 - ((event.y - 25) // square_size)

        # Flip perspective if board is flipped
        if self.flipped:
            file = 7 - file
            rank = 7 - rank

        square = chess.square(file, rank)

        if self.mode == "play":
            # If no square is selected yet, select the piece on the clicked square
            if self.selected_square is None:
                if self.board.piece_at(square):
                    self.selected_square = square
            else:
                # If a square is already selected, attempt to move the piece to the clicked square
                move = chess.Move(self.selected_square, square)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.move_history = self.board.move_stack[:]
                    self.current_move_index = len(self.move_history)
                self.selected_square = None  # Reset selected square

        elif self.mode == "edit":
            # In "edit mode", place the selected piece on the board
            if self.selected_piece:
                self.board.set_piece_at(square, chess.Piece.from_symbol(self.selected_piece))

        elif self.mode == "clear":
            # In "clear mode", remove the piece from the clicked square
            self.board.remove_piece_at(square)

        self.update_board()
        self.update_turn_label()

    def update_turn_label(self):
        """Updates the turn label color based on whose turn it is."""
        if self.board.turn:
            self.turn_label.config(text="White Turn", bg="white", fg="black")
        else:
            self.turn_label.config(text="Black Turn", bg="black", fg="white")

    def update_board(self):
        """Updates the board display with the current position."""
        square_size = 50
        self.canvas.delete("all")  # Clear the canvas for redrawing

        # Draw ranks (1-8) on the left side based on the flipped state
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        if self.flipped:
            ranks.reverse()

        # Draw ranks on the left
        for i, rank_label in enumerate(ranks):
            self.canvas.create_text(15, 25 + i * square_size + square_size // 2, text=rank_label, font=("Arial", 14))

        # Draw files (a-h) at the bottom (no flipping)
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, file_label in enumerate(files):
            self.canvas.create_text(25 + i * square_size + square_size // 2, 435, text=file_label, font=("Arial", 14))

        # Draw the squares
        for rank in range(8):
            for file in range(8):
                color = "#F0D9B5" if (rank + file) % 2 == 0 else "#B58863"
                if self.flipped:
                    rank = 7 - rank  # Flip the rank if the board is flipped
                self.canvas.create_rectangle(25 + file * square_size, 25 + rank * square_size,
                                             25 + (file + 1) * square_size, 25 + (rank + 1) * square_size,
                                             fill=color)

        # Draw the pieces
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_text = PIECE_SYMBOLS[piece.symbol()]
                file = chess.square_file(square)
                rank = 7 - chess.square_rank(square)

                if self.flipped:
                    file = 7 - file
                    rank = 7 - rank

                self.canvas.create_text(25 + file * square_size + square_size // 2,
                                        25 + rank * square_size + square_size // 2,
                                        text=piece_text, font=("Arial", 24))

        # Update the advantage bar if enabled
        if self.advantage_bar_enabled.get():
            self.update_advantage_bar()

    def update_advantage_bar(self):
        """Updates the advantage bar based on Stockfish evaluation."""
        score = self.evaluate_position()  # Retrieve score directly from Stockfish
        self.advantage_bar_canvas.delete("all")
    
        # Advantage ranges from -80 (Black advantage) to +80 (White advantage)
        normalized_score = max(min(score, 80), -80)
    
        # Calculate the position for the advantage bar fill
        white_adv_height = int((80 - normalized_score) / 160 * 400)  # Normalize white height (from 0 to 400 pixels)
        white_adv_height = max(min(white_adv_height, 400), 0)  # Ensure it's constrained between 0 and 400

        # Draw the advantage bar
        self.advantage_bar_canvas.create_rectangle(0, 0, 50, white_adv_height, fill="white")  # White advantage
        self.advantage_bar_canvas.create_rectangle(0, white_adv_height, 50, 400, fill="black")  # Black advantage

        # Display the numerical advantage as text
        advantage_text = f"+{normalized_score:.2f}" if normalized_score > 0 else f"{normalized_score:.2f}"
        self.advantage_label.config(text=f"Advantage: {advantage_text}")

    def evaluate_position(self):
        """Evaluates the current position using Stockfish and returns the advantage."""
        try:
            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
                info = engine.analyse(self.board, chess.engine.Limit(depth=15))
                score = info["score"].relative.score()
                return score / 100 if score is not None else 0
        except Exception as e:
            print(f"Engine error: {str(e)}")
            return 0  # If evaluation fails, return 0

    def previous_move(self):
        """Go back to the previous move in the game history."""
        if self.current_move_index > 0:
            self.current_move_index -= 1
            self.board.set_fen(chess.STARTING_FEN)
            for move in self.move_history[:self.current_move_index]:
                self.board.push(move)
            self.update_board()

    def next_move(self):
        """Go forward to the next move in the game history."""
        if self.current_move_index < len(self.move_history):
            move = self.move_history[self.current_move_index]
            self.board.push(move)
            self.current_move_index += 1
            self.update_board()

    def go_to_first_move(self):
        """Resets the board to the initial position (starting FEN)."""
        self.current_move_index = 0
        self.board.reset()
        self.update_board()

    def go_to_last_move(self):
        """Plays all moves up to the last move in the move history."""
        self.board.reset()
        for move in self.move_history:
            self.board.push(move)
        self.current_move_index = len(self.move_history)
        self.update_board()

    def toggle_play_pause(self):
        """Toggles between playing and pausing the automatic move advancement."""
        if self.playing:
            self.play_pause_button.config(text="▶️")  # Set to play icon
            self.playing = False  # Stop playing
        else:
            self.play_pause_button.config(text="⏸️")  # Set to pause icon
            self.playing = True  # Start playing
            self.auto_play_moves()

    def auto_play_moves(self):
        """Automatically advances through the moves if in playing mode."""
        if self.playing and self.current_move_index < len(self.move_history):
            self.next_move()
            self.root.after(1000, self.auto_play_moves)  # 1000 ms = 1 second between moves
        elif self.current_move_index >= len(self.move_history):
            # Reached the end of the game, so we stop without toggling play/pause state
            self.playing = False
            self.play_pause_button.config(text="▶️")  # Automatically reset button to "Play" state

    def clear_board(self):
        """Clears all pieces from the board."""
        self.board.clear()
        self.update_board()

    def load_fen_or_pgn(self):
        """Loads a position from the FEN or PGN provided in the entry box."""
        input_text = self.input_entry.get()

        # Try loading as FEN
        try:
            self.board.set_fen(input_text)
            self.update_board()
            return
        except ValueError:
            pass  # If it's not a valid FEN, try PGN

        # Try loading as PGN
        try:
            pgn = StringIO(input_text)
            self.game = chess.pgn.read_game(pgn)
            self.board.reset()  # Reset the board to the initial state
            self.move_history = list(self.game.mainline_moves())
            self.current_move_index = 0  # Start from the beginning
            self.update_board()
        except Exception:
            messagebox.showerror("Invalid Input", "Please enter a valid FEN or PGN string.")

    def reset_board(self):
        """Resets the board to the default starting position."""
        self.board.reset()
        self.move_history = []
        self.current_move_index = 0
        self.update_board()

    def flip_board(self):
        """Flips the board, changing the perspective between White and Black."""
        self.flipped = not self.flipped
        self.update_board()

# Create the main window and run the app
if __name__ == '__main__':
    root = tk.Tk()
    ChessApp(root)
    root.mainloop()

