# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 12:21:18 2024

@author: Robin Corbonnois
"""


import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import PhotoImage  # Add support for profile pictures
import chess
import chess.engine
from PIL import Image, ImageTk  # For handling images like profile pictures and flags

VERSION = "chessbot v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Schachspiel")
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="black")
        self.board = chess.Board()
        self.engine_path = r"C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\code\stockfish\stockfish-windows-x86-64-avx2.exe"
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
        self.player_country = "Deutschland"  # Default country
        self.bot_country = "Computer"
        self.player_image = None
        self.bot_image = None
        self.captured_pieces_player = []
        self.captured_pieces_bot = []
        self.create_game_interface()
        self.board.reset()  # Directly start with the game interface
        

    

    def load_profile_image(self, path):
        # Load and resize profile image for display
        image = Image.open(path)
        image = image.resize((50, 50), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def bot_move(self):
        # Bot makes a move
        result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
        if self.board.is_capture(result.move):
            captured_piece = self.board.piece_at(result.move.to_square)
            self.captured_pieces_bot.append(captured_piece.symbol())
        self.board.push(result.move)
        self.update_board()
        self.output_text.insert(tk.END, f"Bot: {result.move}\n")
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            row, col = divmod(king_square, 8)
            self.squares[(7 - row, col)].create_rectangle(0, 0, self.square_size, self.square_size, outline="red", width=5)

    def display_difficulty_options(self):
        # Display difficulty options for bot play
        self.clear_screen()
        self.difficulty_prompt = tk.Frame(self.root, bg="black")
        self.difficulty_prompt.pack(expand=True)
        tk.Label(self.difficulty_prompt, text="Wähle den Schwierigkeitsgrad", font=("Arial", 20), bg="black", fg="white").pack(pady=10)

        self.easy_button = tk.Button(self.difficulty_prompt, text="Einfach", font=("Arial", 16), command=lambda: self.start_game(800), bg="gray", fg="white")
        self.easy_button.pack(pady=10, fill=tk.X)

        self.medium_button = tk.Button(self.difficulty_prompt, text="Mittel", font=("Arial", 16), command=lambda: self.start_game(1200), bg="gray", fg="white")
        self.medium_button.pack(pady=10, fill=tk.X)

        self.hard_button = tk.Button(self.difficulty_prompt, text="Schwer", font=("Arial", 16), command=lambda: self.start_game(1800), bg="gray", fg="white")
        self.hard_button.pack(pady=10, fill=tk.X)

    def start_game(self, elo):
        # Set the elo and reset the game board
        self.elo = elo
        self.mode = "bot"
        self.board.reset()
        self.captured_pieces_player.clear()
        self.captured_pieces_bot.clear()
        self.create_game_interface()  # Recreate the game interface to avoid deletion errors
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Weiß ist am Zug\n")
        self.play_bot_button.configure(bg="yellow")  # Highlight the Play against Bot button
        self.play_friend_button.configure(bg="gray")  # Reset the friend button highlight

    def handle_square_click(self, row, col):
        # Handle click event for each square, either player or bot move
        selected_square = chess.square(col, 7 - row)
        if self.selected_piece is not None:
            move = chess.Move(self.selected_piece, selected_square)
            if move in self.board.legal_moves:
                if self.board.is_capture(move):
                    captured_piece = self.board.piece_at(move.to_square)
                    self.captured_pieces_player.append(captured_piece.symbol())
                self.board.push(move)
                self.selected_piece = None
                self.update_board()
                self.output_text.insert(tk.END, f"Move: {move}\n")
                if self.board.is_check():
                    king_square = self.board.king(self.board.turn)
                    row, col = divmod(king_square, 8)
                    self.squares[(7 - row, col)].create_rectangle(0, 0, self.square_size, self.square_size, outline="red", width=5)
                if self.mode == "bot" and not self.board.turn:
                    self.bot_move()
            else:
                self.selected_piece = None  # Deselect if move is not legal
                self.update_board()  # Remove any highlighted moves
        else:
            piece = self.board.piece_at(selected_square)
            if piece and piece.color == self.board.turn:
                self.selected_piece = selected_square
                self.highlight_moves(selected_square)

    def start_friend_game(self):
        # Start a game against a friend
        self.mode = "friend"
        self.board.reset()
        self.captured_pieces_player.clear()
        self.captured_pieces_bot.clear()
        self.create_game_interface()  # Recreate the game interface to avoid deletion errors
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Weiß ist am Zug\n")
        self.play_friend_button.configure(bg="yellow")  # Highlight the Play against Friend button
        self.play_bot_button.configure(bg="gray")  # Reset the bot button highlight
        self.top_label.config(text="Gegner")  # Update label to indicate opponent in friend mode

    def analyze_game(self):
        # Placeholder function for game analysis
        messagebox.showinfo("Analyse", "Spielanalyse ist noch nicht implementiert.")

    def toggle_window_size(self):
        # Toggle window size between normal and bigger
        if self.root.state() == "normal":
            self.root.state("zoomed")
        else:
            self.root.state("normal")

    def highlight_moves(self, square):
        # Highlight possible moves for the selected piece with a filled oval
        moves = list(self.board.legal_moves)
        for move in moves:
            if move.from_square == square:
                row, col = divmod(move.to_square, 8)
                self.squares[(7 - row, col)].create_oval(35, 35, self.square_size - 35, self.square_size - 35, fill="green", outline="")

    def update_board(self):
        # Ensure that the piece banks are initialized before updating
        if not hasattr(self, 'bot_bank_canvas') or not hasattr(self, 'player_bank_canvas'):
            return
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
        self.update_piece_banks()
        self.update_advantage()

    def update_piece_banks(self):
        # Update piece banks for both player and bot
        self.bot_bank_canvas.delete("all")
        self.player_bank_canvas.delete("all")

        piece_x_offset = 10
        for idx, piece_symbol in enumerate(self.captured_pieces_bot):
            self.bot_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")
        for idx, piece_symbol in enumerate(self.captured_pieces_player):
            self.player_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")

    def update_advantage(self):
        # Update advantage calculation at the end of the piece bank
        player_advantage = len(self.captured_pieces_bot) - len(self.captured_pieces_player)
        if player_advantage > 0:
            advantage_text = f"+{player_advantage}"
            self.bot_bank_canvas.create_text(180, 25, text=advantage_text, font=("Arial", 16), fill="red")  # Adjusted position for compact fit
        elif player_advantage < 0:
            advantage_text = f"+{-player_advantage}"
            self.player_bank_canvas.create_text(180, 25, text=advantage_text, font=("Arial", 16), fill="red")  # Adjusted position for compact fit
        # Update the piece banks for both the player and the bot
        self.bot_bank_canvas.delete("all")
        self.player_bank_canvas.delete("all")

        piece_x_offset = 10
        for idx, piece_symbol in enumerate(self.captured_pieces_bot):
            self.bot_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")
        
        for idx, piece_symbol in enumerate(self.captured_pieces_player):
            self.player_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")

    def show_rules(self):
        # Display chess rules in a new window
        messagebox.showinfo("Schachregeln", "Hier sind die Schachregeln: ...")

    def show_documentation(self):
        # Display documentation in a new window
        messagebox.showinfo("Dokumentation", "Hier ist die Dokumentation zum Schachbot: ...")

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
