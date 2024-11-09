# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 22:38:07 2024

@author: Robin Corbonnois
"""

import tkinter as tk
from tkinter import messagebox
import chess
import chess.engine

VERSION = "chessbot 14.07 vquit"

class ChessApp:
    def __init__(self, root, player_name="Player 1", bot_name="Bot", elo=1200):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Chess Game")
        self.board = chess.Board()
        self.engine_path = r"C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\code\stockfish\stockfish-windows-x86-64-avx2.exe"
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.squares = {}
        self.selected_piece = None
        self.elo = elo
        self.mode = "bot"  # Set default mode to bot play
        self.player_name = player_name
        self.bot_name = bot_name
        self.create_board()  # Create the board initially

    def create_board(self):
        # Create the visual representation of the chessboard with player names
        self.clear_screen()

        # Frame for the bot's name and captured pieces
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP)
        self.top_label = tk.Label(self.top_frame, text=self.bot_name, font=("Arial", 16), pady=10)
        self.top_label.pack(side=tk.LEFT)

        # Frame for the chessboard
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        for row in range(8):
            for col in range(8):
                square = tk.Canvas(self.board_frame, width=60, height=60)
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.on_square_click(r, c))
                self.squares[(row, col)] = square

        # Frame for the player's name and captured pieces
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM)
        self.bottom_label = tk.Label(self.bottom_frame, text=self.player_name, font=("Arial", 16), pady=10)
        self.bottom_label.pack(side=tk.LEFT)

        # Create a reset button next to the board
        self.reset_button = tk.Button(self.root, text="Reset Board", font=("Arial", 12), command=self.reset_board)
        self.reset_button.pack(pady=10)

        # Update the board to reflect the current game state
        self.update_board()

    def update_board(self):
        # Update the chessboard's visual representation
        pieces = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        for row in range(8):
            for col in range(8):
                square = self.squares[(row, col)]
                square.delete("all")
                color = "white" if (row + col) % 2 == 0 else "gray"
                square.create_rectangle(0, 0, 60, 60, outline="black", fill=color)
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    symbol = pieces[piece.symbol()]
                    square.create_text(30, 30, text=symbol, font=("Arial", 24), anchor="center")

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
                if not self.board.is_game_over():
                    if self.board.turn == chess.BLACK:
                        self.bot_move()
                else:
                    messagebox.showinfo("Game Over", f"Result: {self.board.result()}")
            else:
                self.selected_piece = None
                self.update_board()
                messagebox.showwarning("Invalid Move", "This is not a legal move.")

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
        if self.board.is_game_over():
            messagebox.showinfo("Game Over", f"Result: {self.board.result()}")

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
        self.engine.quit()
        self.root.destroy()

if __name__ == "__main__":
    # Main program: Initialize and start the GUI
    root = tk.Tk()
    app = ChessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
