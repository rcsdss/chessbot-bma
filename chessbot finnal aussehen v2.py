# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 23:57:43 2024

@author: Robin
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import chess
import chess.engine

VERSION = "chessbot v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Schachspiel")
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="black")
        self.board = chess.Board()
        self.engine_path = r"C:\\Users\\Robin\\OneDrive - Schulen Biberist\\Desktop\\this-is\\stockfish\\stockfish-windows-x86-64-avx2.exe"
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
        self.create_game_interface()  # Directly start with the game interface
        self.board.reset()
        self.update_board()

    def create_game_interface(self):
        # Create game interface layout
        self.clear_screen()

        # General frame that holds everything, helps centralize components
        self.general_frame = tk.Frame(self.root, bg="black")
        self.general_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Configure grid layout for the general frame
        self.general_frame.grid_rowconfigure(0, weight=1)
        self.general_frame.grid_rowconfigure(1, weight=8)
        self.general_frame.grid_rowconfigure(2, weight=1)
        self.general_frame.grid_columnconfigure(0, weight=4)
        self.general_frame.grid_columnconfigure(1, weight=10)
        self.general_frame.grid_columnconfigure(2, weight=4)

        # Create left menu frame and align it vertically to the chessboard
        self.menu_frame = tk.Frame(self.general_frame, bg="black")
        self.menu_frame.grid(row=1, column=0, sticky="ns", pady=(200))  # pady=(top, bottom)
        self.general_frame.grid_columnconfigure(0, weight=5)  # Make sure the menu frame takes equal space for better centering

        welcome_label = tk.Label(self.menu_frame, text="Br Bot GUI", font=("Arial", 20), bg="black", fg="white")
        welcome_label.pack(pady=10)

        self.play_bot_button = tk.Button(self.menu_frame, text="Gegen den Bot spielen", font=("Arial", 16), command=self.display_difficulty_options, bg="gray", fg="white")
        self.play_bot_button.pack(pady=10, fill=tk.X)

        self.play_friend_button = tk.Button(self.menu_frame, text="Gegen einen Freund spielen", font=("Arial", 16), command=self.start_friend_game, bg="gray", fg="white")
        self.play_friend_button.pack(pady=10, fill=tk.X)

        self.analyze_button = tk.Button(self.menu_frame, text="Spiel analysieren", font=("Arial", 16), command=self.analyze_game, bg="gray", fg="white")
        self.analyze_button.pack(pady=10, fill=tk.X)

        self.bigger_window_button = tk.Button(self.menu_frame, text="Chessboard vergrößern", font=("Arial", 14), command=self.toggle_window_size, bg="gray", fg="white")
        self.bigger_window_button.pack(pady=10, fill=tk.X)

        self.rules_button = tk.Button(self.menu_frame, text="Schachregeln", font=("Arial", 14), command=self.show_rules, bg="gray", fg="white")
        self.rules_button.pack(pady=10, fill=tk.X)

        self.documentation_button = tk.Button(self.menu_frame, text="Dokumentation", font=("Arial", 14), command=self.show_documentation, bg="gray", fg="white")
        self.documentation_button.pack(pady=10, fill=tk.X)

        self.exit_button = tk.Button(self.menu_frame, text="Beenden (ESC)", font=("Arial", 14), command=self.root.quit, bg="gray", fg="white")
        self.exit_button.pack(pady=10, fill=tk.X)

        # Frame for the chessboard, centered in the middle
        self.board_frame = tk.Frame(self.general_frame, bg="black")
        self.board_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        # Calculate square size dynamically based on the available space
        self.square_size = 110  # Adjusted size for better visibility and layout

        for row in range(8):
            for col in range(8):
                square = tk.Canvas(self.board_frame, width=self.square_size, height=self.square_size, highlightthickness=0)
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.on_square_click(r, c))
                self.squares[(row, col)] = square

        # Draw the initial board with pieces
        self.update_board()

        # Frame for player's information and clock - aligned above the board
        self.top_info_frame = tk.Frame(self.general_frame, bg="black")
        self.top_info_frame.grid(row=0, column=1, sticky="e", padx=(0, 20))
        self.top_label = tk.Label(self.top_info_frame, text=f"{self.bot_name}", font=("Arial", 16), fg="green", bg="black")
        self.top_label.pack(side=tk.LEFT, padx=5)
        self.black_clock = tk.Label(self.top_info_frame, text="10:00", font=("Arial", 14), fg="black", bg="#FFC107", padx=10)
        self.black_clock.pack(side=tk.LEFT, padx=5)

        # Frame for opponent's information and clock - aligned below the board
        self.bottom_info_frame = tk.Frame(self.general_frame, bg="black")
        self.bottom_info_frame.grid(row=2, column=1, sticky="w", padx=(20, 0))
        self.white_clock = tk.Label(self.bottom_info_frame, text="10:00", font=("Arial", 14), fg="white", bg="#4CAF50", padx=10)
        self.white_clock.pack(side=tk.LEFT, padx=5)
        self.bottom_label = tk.Label(self.bottom_info_frame, text=f"{self.player_name}", font=("Arial", 16), fg="green", bg="black")
        self.bottom_label.pack(side=tk.LEFT, padx=5)

        # Text box for move history or bot output - right of the board
        self.output_frame = tk.Frame(self.general_frame, bg="black")
        self.output_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=20)
        self.general_frame.grid_columnconfigure(2, weight=5)  # Make sure the right frame aligns properly and has enough space
        self.output_text = scrolledtext.ScrolledText(self.output_frame, width=30, height=40, font=("Arial", 12), bg="black", fg="white", wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Willkommen beim Schachbot! Weiß ist am Zug\n")

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

    def toggle_window_size(self):
        # Toggle window size between normal and bigger
        if self.root.state() == "normal":
            self.root.state("zoomed")
        else:
            self.root.state("normal")

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
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                square.create_rectangle(0, 0, self.square_size, self.square_size, outline="black", fill=color)
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    symbol = pieces[piece.symbol()]
                    square.create_text(self.square_size // 2, self.square_size // 2, text=symbol, font=("Arial", int(self.square_size * 0.5)), anchor="center")

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
