# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 17:52:38 2024

@author: Robin
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import chess
import chess.engine

VERSION = "chessbot v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Schachspiel")
        self.root.geometry("800x600")
        self.board = chess.Board()
        self.engine_path = self.ask_for_engine_path()  # Ask for Stockfish path
        if not self.engine_path:
            messagebox.showerror("Fehler", "Kein Pfad zur Engine ausgewählt. Das Programm wird beendet.")
            root.quit()
        else:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.squares = {}
        self.selected_piece = None
        self.elo = 800  # Start in easy mode by default
        self.mode = "bot"  # Set default mode to bot play
        self.player_name = "Spieler 1"
        self.bot_name = "Bot"
        self.create_game_interface()  # Directly create the game interface
        self.board.reset()
        self.update_board()
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Weiß ist am Zug\n")

    def ask_for_engine_path(self):
        # Open a dialog to ask for the path of the Stockfish engine
        return filedialog.askopenfilename(title="Wähle die Stockfish-Engine aus", filetypes=[("Executable Files", "*.exe")])

    def create_game_interface(self):
        # Create left menu frame
        self.menu_frame = tk.Frame(self.root, bg="black")
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

        welcome_label = tk.Label(self.menu_frame, text="Willkommen", font=("Arial", 20), bg="black", fg="white")
        welcome_label.pack(pady=10)

        self.play_bot_button = tk.Button(self.menu_frame, text="Gegen den Bot spielen", font=("Arial", 16), command=self.display_difficulty_options, bg="gray", fg="white")
        self.play_bot_button.pack(pady=10, fill=tk.X)

        self.play_friend_button = tk.Button(self.menu_frame, text="Gegen einen Freund spielen", font=("Arial", 16), command=self.start_friend_game, bg="gray", fg="white")
        self.play_friend_button.pack(pady=10, fill=tk.X)

        self.analyze_button = tk.Button(self.menu_frame, text="Spiel analysieren", font=("Arial", 16), command=self.analyze_game, bg="gray", fg="white")
        self.analyze_button.pack(pady=10, fill=tk.X)

        self.bigger_window_button = tk.Button(self.menu_frame, text="Größeres Fenster", font=("Arial", 14), command=self.toggle_window_size, bg="gray", fg="white")
        self.bigger_window_button.pack(pady=10, fill=tk.X)

        self.exit_button = tk.Button(self.menu_frame, text="Beenden (ESC)", font=("Arial", 14), command=self.root.quit, bg="gray", fg="white")
        self.exit_button.pack(pady=10, fill=tk.X)

        # Frame for the bot's name and turn indicator
        self.top_frame = tk.Frame(self.root, bg="black")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.top_label = tk.Label(self.top_frame, text=f"Schwarz: {self.bot_name}", font=("Arial", 16), fg="green", bg="black", pady=10)
        self.top_label.pack(side=tk.LEFT, expand=True, anchor="center")

        # Create turn indicator
        self.turn_indicator = tk.Label(self.top_frame, text="Weiß ist am Zug", font=("Arial", 16, "bold"), fg="white", bg="black", pady=10, relief=tk.RAISED, padx=10)
        self.turn_indicator.pack(side=tk.RIGHT, padx=10, expand=True, anchor="center")

        # Frame for the chessboard
        self.board_frame = tk.Frame(self.root, bg="black")
        self.board_frame.pack(side=tk.LEFT, padx=20, pady=20)

        for row in range(8):
            for col in range(8):
                square = tk.Canvas(self.board_frame, width=60, height=60, highlightthickness=0)
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.on_square_click(r, c))
                self.squares[(row, col)] = square

        # Draw the initial board with pieces
        self.update_board()

        # Frame for the player's name and captured pieces
        self.bottom_frame = tk.Frame(self.root, bg="black")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_label = tk.Label(self.bottom_frame, text=f"Weiß: {self.player_name}", font=("Arial", 16), fg="green", bg="black", pady=10)
        self.bottom_label.pack(side=tk.LEFT)

        # Text box for move history or bot output
        self.output_frame = tk.Frame(self.root, bg="black")
        self.output_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
        self.output_text = scrolledtext.ScrolledText(self.output_frame, width=30, height=20, font=("Arial", 12), bg="black", fg="white", wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Weiß ist am Zug\n")

    def display_difficulty_options(self):
        # Display difficulty options for bot play
        self.clear_screen()
        self.difficulty_prompt = tk.Frame(self.root, bg="black")
        self.difficulty_prompt.pack(expand=True)
        tk.Label(self.difficulty_prompt, text="Wähle den Schwierigkeitsgrad", font=("Arial", 16), bg="black", fg="white").pack(pady=10)

        self.easy_button = tk.Button(self.difficulty_prompt, text="Einfach", font=("Arial", 16), command=lambda: self.start_game(800), bg="gray", fg="white")
        self.easy_button.pack(pady=5, fill=tk.X)

        self.medium_button = tk.Button(self.difficulty_prompt, text="Mittel", font=("Arial", 16), command=lambda: self.start_game(1200), bg="gray", fg="white")
        self.medium_button.pack(pady=5, fill=tk.X)

        self.hard_button = tk.Button(self.difficulty_prompt, text="Schwer", font=("Arial", 16), command=lambda: self.start_game(1800), bg="gray", fg="white")
        self.hard_button.pack(pady=5, fill=tk.X)

    def start_game(self, elo):
        # Start the game with the selected difficulty
        self.elo = elo
        self.difficulty_prompt.destroy()  # Remove difficulty selection
        self.create_game_interface()
        self.board.reset()
        self.update_board()
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Weiß ist am Zug\n")

    def toggle_window_size(self):
        # Toggle window size between normal and bigger
        if self.root.state() == "normal":
            self.root.state("zoomed")
        else:
            self.root.state("normal")

    def start_friend_game(self):
        # Start a game against a friend
        self.mode = "friend"
        self.board.reset()
        self.update_board()
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Weiß ist am Zug\n")

    def analyze_game(self):
        # Placeholder function for game analysis
        messagebox.showinfo("Analyse", "Spielanalyse ist noch nicht implementiert.")

    def update_board(self):
        # Update the chessboard's visual representation
        if self.mode == "friend":
                # Toggle turn indicator for friend play
                if self.board.turn == chess.WHITE:
                        self.turn_indicator.config(text="Weiß ist am Zug", fg="white", bg="#4CAF50")  # Green indicator for white's turn
                else:
                        self.turn_indicator.config(text="Schwarz ist am Zug", fg="black", bg="#FFC107")  # Yellow indicator for black's turn
        else:
                # Update the turn indicator for bot play
                if self.board.turn == chess.WHITE:
                        self.turn_indicator.config(text="Weiß ist am Zug", fg="white", bg="#4CAF50")  # Green indicator for white's turn
                else:
                        self.turn_indicator.config(text="Schwarz ist am Zug", fg="black", bg="#FFC107")  # Yellow indicator for black's turn
        pieces = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        for row in range(8):
            for col in range(8):
                square = self.squares[(row, col)]
                square.delete("all")
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                square.create_rectangle(0, 0, 60, 60, outline="black", fill=color)
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    symbol = pieces[piece.symbol()]
                    square.create_text(30, 30, text=symbol, font=("Arial", 24), anchor="center")

        # Update the turn indicator
        if self.board.turn == chess.WHITE:
            self.turn_indicator.config(text="Weiß ist am Zug", fg="white", bg="#4CAF50")  # Green indicator for white's turn
        else:
            self.turn_indicator.config(text="Schwarz ist am Zug", fg="black", bg="#FFC107")  # Yellow indicator for black's turn

    def on_square_click(self, row, col):
        # Handle the event when a square on the board is clicked
        square = chess.square(col, 7 - row)
        if self.selected_piece is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_piece = square
                self.highlight_moves(square)
        else:
            move = chess.Move(self.selected_piece, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_piece = None
                self.update_board()
                self.output_text.insert(tk.END, f"Spieler hat gezogen: {move}\n")
                if not self.board.is_game_over():
                    if self.mode == "bot" and self.board.turn == chess.BLACK:
                        self.bot_move()
                else:
                    messagebox.showinfo("Spiel beendet", f"Ergebnis: {self.board.result()}")
                    self.output_text.insert(tk.END, f"Spiel beendet: {self.board.result()}\n")
            else:
                self.selected_piece = None
                self.update_board()
                messagebox.showwarning("Ungültiger Zug", "Das ist kein gültiger Zug.")

    def highlight_moves(self, square):
        # Highlight possible moves for the selected piece
        moves = list(self.board.legal_moves)
        for move in moves:
            if move.from_square == square:
                row, col = divmod(move.to_square, 8)
                self.squares[(7 - row, col)].create_oval(25, 25, 35, 35, fill="green", outline="")

    def bot_move(self):
        # Execute the bot's move
        time_limit = self.get_time_limit(self.elo)
        result = self.engine.play(self.board, chess.engine.Limit(time=time_limit))
        self.board.push(result.move)
        self.update_board()
        self.output_text.insert(tk.END, f"Bot hat gezogen: {result.move}\n")
        if self.board.is_game_over():
            messagebox.showinfo("Spiel beendet", f"Ergebnis: {self.board.result()}")
            self.output_text.insert(tk.END, f"Spiel beendet: {self.board.result()}\n")

    def get_time_limit(self, elo):
        # Determine the time limit for the bot based on its ELO rating
        if elo < 1000:
            return 0.1  # 0.1 seconds for beginners
        elif elo < 1400:
            return 0.5  # 0.5 seconds for intermediate players
        elif elo < 1800:
            return 1.0  # 1.0 seconds for advanced players
        elif elo < 2200:
            return 2.0  # 2.0 seconds for experts
        else:
            return 5.0  # 5.0 seconds for masters

    def reset_board(self):
        # Reset the chessboard to the starting position
        self.board.reset()
        self.update_board()

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

if __name__ == "__main__":
    # Main program: Initialize and start the GUI
    root = tk.Tk()
    app = ChessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
