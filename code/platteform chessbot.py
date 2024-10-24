# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 10:31:42 2024

@author: Robin Corbonnois
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import chess
import chess.engine
import os

VERSION = "chessbot platteforme v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Willkommen zu dem BR ChessBot v2")  # Updated title for clarity
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="black")
        self.board = chess.Board()
       
        # Set game mode to default ('einfach' - easy)
        self.game_mode = tk.StringVar(value="einfach")

        # Set relative path use os.path for Stockfish engine
        self.engine_path = os.path.join(os.getcwd(), "stockfish", "stockfish-windows-x86-64-avx2.exe")
        if not os.path.exists(self.engine_path):
            # If engine not found, prompt the user
            self.engine_path = self.browse_for_engine()  # Prompt user to select the engine path
            if not self.engine_path:
                messagebox.showerror("Fehler", "Kein Pfad zur Engine ausgewählt. Das Programm wird beendet.")
                root.quit()
            else:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        else:
            # If the engine path exists, initialize it
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

        # Initialize various game state variables
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
        self.player_time_left = None
        self.bot_time_left = None
        self.player_timer_running = False
        self.bot_timer_running = False
        self.timed_game = False  # Track if the game is timed
        self.first_move_played = False  # Track if the first move has been played

        # Create the user interface for the game
        self.create_game_interface()


    def browse_for_engine(self):
        # Function to prompt user to browse for the Stockfish engine
        engine_path = filedialog.askopenfilename(title="Stockfish-Engine auswählen", filetypes=[("Ausführbare Dateien", "*.exe"), ("Alle Dateien", "*.*")])
        return engine_path

    def create_game_interface(self):
        # Create the in-game interface with all controls
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
    
        # Game mode selection frame (Radio buttons)
        self.mode_frame = tk.Frame(self.general_frame, bg="black")
        self.mode_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 200))  # Adjust padding to move the menu up and closer
        self.game_mode = tk.StringVar(value="einfach")  # Set default mode to "einfach"
    
        # Description label centered at the top of the mode frame
        self.description_label = tk.Label(self.mode_frame, text="Chessbot Br", font=("Comic Sans MS", 24, "bold"), bg="black", fg="white")
        self.description_label.pack(side="top", anchor="center", expand=True, padx=20, pady=(250, 5))  # Reduced padding between label and radio buttons
    
        # Container frame for the radio buttons to center them vertically relative to the description label
        self.radio_buttons_frame = tk.Frame(self.mode_frame, bg="black")
        self.radio_buttons_frame.pack(side="top", anchor="center", expand=False, pady=(0, 5))  # Reduced top padding to bring radio buttons closer to the label
    
        # Creating Radio buttons for different game modes
        tk.Radiobutton(self.radio_buttons_frame, text="👼 Gegen Bot spielen (Einfach)", variable=self.game_mode, value="einfach",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="👴 Gegen Bot spielen (Mittel)", variable=self.game_mode, value="mittel",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="🏋 Gegen Bot spielen (Schwer)", variable=self.game_mode, value="schwer",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="👥 Gegen einen Freund spielen", variable=self.game_mode, value="freund",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        # Play Button, centered below the radio buttons, with reduced spacing
        self.play_button = tk.Button(self.mode_frame, text="▶ Spielen", font=("Arial", 20), bg="green", fg="white", command=self.start_game, width=10)
        self.play_button.pack(pady=(0, 5))  # Reduced padding to bring the button closer to the radio buttons
    
       # Quit Button, directly below the play button
        self.quit_button = tk.Button(self.mode_frame, text="⛔ Beenden", font=("Arial", 20), bg="red", fg="white", command=self.on_closing, width=10)
        self.quit_button.pack(pady=(10, 5))  # Slight top padding to create space below the play button
        
        # Update the GUI to ensure all elements are displayed correctly
        self.root.update()

   
        # Timed game toggle button (removed and replaced with clock label activation)
        self.timed_button_active = False


        # Top information frame for bot details (swapped position)
        self.top_info_frame = tk.Frame(self.general_frame, bg="black")
        self.top_info_frame.grid(row=0, column=1, sticky="nsew")

        # Bot piece bank (placed behind bot info)
        self.bot_bank_frame = tk.Frame(self.top_info_frame, bg="black")
        self.bot_bank_frame.place(x=110, y=50)  # Adjust x, y values for exact positioning
        self.bot_bank_canvas = tk.Canvas(self.bot_bank_frame, width=400, height=50, bg="black", highlightthickness=0)
        self.bot_bank_canvas.pack()

        # Bot information (top)
        self.bot_photo_label = tk.Label(self.top_info_frame, text="🤖", font=("Arial", 50), bg="black", fg="white")
        self.bot_photo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.bot_name_label = tk.Label(self.top_info_frame, text=f"{self.bot_name} ({self.bot_elo})", font=("Arial", 16), fg="white", bg="black")
        self.bot_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.bot_flag_label = tk.Label(self.top_info_frame, text="🇨🇭", font=("Arial", 16), bg="black", fg="white")
        self.bot_flag_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.bot_clock_button = tk.Label(self.top_info_frame, text="⏰", font=("Arial", 16), fg="black", bg="red")
        self.bot_clock_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.bot_clock_button.bind("<Button-1>", lambda event: self.toggle_clock() if not self.timed_button_active else None)

        # Player information (bottom)
        self.bottom_info_frame = tk.Frame(self.general_frame, bg="black")
        self.bottom_info_frame.grid(row=2, column=1, sticky="nsew")

        # Player piece bank (placed behind player info)
        self.player_bank_frame = tk.Frame(self.bottom_info_frame, bg="black")
        self.player_bank_frame.place(x=110, y=50)
        self.player_bank_canvas = tk.Canvas(self.player_bank_frame, width=400, height=50, bg="black", highlightthickness=0)
        self.player_bank_canvas.pack()

        self.player_photo_label = tk.Label(self.bottom_info_frame, text="👤", font=("Arial", 50), bg="black", fg="white")
        self.player_photo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.player_name_label = tk.Label(self.bottom_info_frame, text=f"{self.player_name} ({self.player_elo})", font=("Arial", 16), fg="white", bg="black")
        self.player_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.player_flag_label = tk.Label(self.bottom_info_frame, text="🇨🇭", font=("Arial", 16), bg="black", fg="white")
        self.player_flag_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.player_clock_button = tk.Label(self.bottom_info_frame, text="⏰", font=("Arial", 16), fg="black", bg="red")
        self.player_clock_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.player_clock_button.bind("<Button-1>", lambda event: self.toggle_clock())

        # Frame for the chessboard
        self.board_frame = tk.Frame(self.general_frame, bg="black")
        self.board_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Create chessboard
        self.square_size = 100  # Adjust size accordingly
        for row in range(8):
            for col in range(8):
                square = tk.Canvas(self.board_frame, width=self.square_size, height=self.square_size, highlightthickness=0, bg="gray")  # Initially disabled and grayed out
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.handle_square_click(r, c))
                self.squares[(row, col)] = square

        # Frame for move history or bot output
        self.output_frame = tk.Frame(self.general_frame, bg="black")
        self.output_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.output_frame, width=30, height=40, font=("Arial", 12), bg="black", fg="white", wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Willkommen beim Schachbot! Wählen Sie zuerst einen Spielmodus und klicken Sie auf Spielen, um zu beginnen.")
        self.output_text.configure(state='disabled')  # Disable writing

        # Add the "Aufgeben" button to allow changing the mode after starting the game
        self.abandon_button = tk.Button(self.output_frame, text="Aufgeben / Modus ändern", font=("Arial", 16), command=self.reset_game, bg="blue", fg="white")
        self.abandon_button.pack(pady=5, fill=tk.X)

        self.disable_board()  # Disable board initially
        self.update_board()
    
    def update_selected_mode_display(self):
        # Display the selected mode in the output text area and print to console (Spyder)
        current_mode = self.game_mode.get()
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, f"\nModus ausgewählt: {current_mode}")
        self.output_text.configure(state='disabled')
        print(f"Modus ausgewählt: {current_mode}")  # Print to console for Spyder or debugging
        


    
    def toggle_clock(self):
        # Toggle between activating and deactivating the timed game by clicking on the clock icon
        if not self.timed_button_active:
            self.timed_button_active = True
            self.timed_game = True
            self.player_time_left = 180 if self.timed_button_active else None  # Set default time to 3 minutes
            self.bot_time_left = 180 if self.timed_button_active else None
            self.bot_clock_button.config(bg="orange", text="⏰ 03:00")
            self.player_clock_button.config(bg="orange", text="⏰ 03:00")
        else:
            self.timed_button_active = False
            self.timed_game = False
            self.player_time_left = None
            self.bot_time_left = None
            self.bot_clock_button.config(bg="red", text="⏰")
            self.player_clock_button.config(bg="red", text="⏰")
        self.update_timer_display('player')
        self.update_timer_display('bot')

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
        self.player_bank_canvas.delete("all")
        self.bot_bank_canvas.delete("all")

        piece_x_offset = 10
        for idx, piece_symbol in enumerate(self.captured_pieces_bot):
            self.player_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")
        for idx, piece_symbol in enumerate(self.captured_pieces_player):
            self.bot_bank_canvas.create_text(piece_x_offset + idx * 20, 25, text=self.pieces.get(piece_symbol, piece_symbol), font=("Arial", 16), fill="white")

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

    def start_game(self):
        # Function to start a game with selected difficulty
        difficulty = self.game_mode.get()
        
        # Check if it's a friend mode, call start_friend_game
        if difficulty == "freund":
            self.start_friend_game()
            return
    
        # Update opponent (bot) information for bot mode
        self.bot_name = "Bot"
        self.bot_elo = 1200  # Reset elo for bot
        self.bot_name_label.configure(text=f"{self.bot_name} ({self.bot_elo})")
        self.bot_photo_label.configure(text="🤖")  # Change icon to bot
    
        # Set bot parameters based on selected difficulty
        if difficulty == "einfach":
            self.bot_time_limit = 0.2
            self.bot_depth = 5
        elif difficulty == "mittel":
            self.bot_time_limit = 0.5
            self.bot_depth = 10
        elif difficulty == "schwer":
            self.bot_time_limit = 1.0
            self.bot_depth = 20
    
        # Initialize timers if the game is timed
        if self.timed_game:
            self.player_time_left = 180  # 3 minutes
            self.bot_time_left = 180  # 3 minutes
    
        # Output status message
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, f"\nSpiel startet mit {difficulty} Schwierigkeitsgrad.")
        self.output_text.configure(state='disabled')
        
        # Enable the game
        self.game_started = True
        self.enable_board()  # Enable the board after starting the game
        # No longer start timers here, wait until first move is played
    
    
    def start_friend_game(self):
        # Function to start a game against a friend
        self.bot_name = "Spieler 2"
        self.bot_elo = 800  # Set a different Elo rating for the friend
        self.bot_name_label.configure(text=f"{self.bot_name} ({self.bot_elo})")
        self.bot_photo_label.configure(text="👤")  # Change the bot icon to a player icon
    
        # Output status message for starting a friend game
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, "\nSpiel gegen einen Freund startet.")
        self.output_text.configure(state='disabled')
        
        # Initialize timers if the game is timed
        if self.timed_game:
            self.player_time_left = 180  # 3 minutes for Player 1
            self.bot_time_left = 180  # 3 minutes for Player 2
        
        # Enable the game
        self.game_started = True
        self.enable_board()  # Enable the board after starting the game
        # No longer start timers here, wait until first move is played

    def reset_game(self):
        # Fonction pour réinitialiser le jeu
        self.board.reset()
        self.reset_piece_banks()
        self.update_board()
        self.disable_board()  # Désactivez l'échiquier
        self.game_started = False
        self.first_move_played = False
        self.player_timer_running = False
        self.bot_timer_running = False
    
        # Conserver le mode de jeu sélectionné (ne pas réinitialiser game_mode)
        current_mode = self.game_mode.get()
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, f"\nLe jeu a été réinitialisé. Mode conservé: {current_mode}")
        self.output_text.configure(state='disabled')
    
        # Réinitialiser l'état des horloges
        self.update_timer_display('player')
        self.update_timer_display('bot')
        self.timed_game = False
        self.timed_button_active = False
        self.bot_clock_button.config(bg="red", text="⏰")
        self.player_clock_button.config(bg="red", text="⏰")
        self.root.update_idletasks()

    def start_timers(self):
        # Start player or bot timers depending on whose turn it is
        if self.board.turn == chess.WHITE:
            self.start_player_timer()
        else:
            self.start_bot_timer()

    def start_player_timer(self):
        if self.player_time_left is not None and self.player_time_left > 0 and self.board.turn == chess.WHITE and self.game_started:
            self.player_time_left -= 1
            self.update_timer_display('player')
            self.player_timer_running = True
            self.root.after(1000, self.start_player_timer)  # Decrease by 1 second each time  # Decrease by 1 second each time
        elif self.player_time_left == 0:
            self.game_started = False
            self.player_timer_running = False
            if not hasattr(self, 'end_game_displayed') or not self.end_game_displayed:
                self.end_game_displayed = True
                self.display_end_game_popup("Schwarz hat gewonnen!", "durch Zeitablauf")

    def start_bot_timer(self):
        if self.bot_time_left is not None and self.bot_time_left > 0 and self.board.turn == chess.BLACK and self.game_started:
            self.bot_time_left -= 1
            self.update_timer_display('bot')
            self.bot_timer_running = True
            self.root.after(1000, self.start_bot_timer)  # Decrease by 1 second each time  # Decrease by 1 second each time
        elif self.bot_time_left == 0:
            self.game_started = False
            self.bot_timer_running = False
            if not hasattr(self, 'end_game_displayed') or not self.end_game_displayed:
                self.end_game_displayed = True
                self.display_end_game_popup("Weiß hat gewonnen!", "durch Zeitablauf")

    def update_timer_display(self, player_type):
        if player_type == 'player':
            if self.player_time_left is not None:
                minutes, seconds = divmod(self.player_time_left, 60)
                self.player_clock_button.config(text=f"⏰ {minutes:02d}:{seconds:02d}", bg="white" if self.board.turn == chess.WHITE else "gray")
            else:
                self.player_clock_button.config(text="⏰", bg="red")
        elif player_type == 'bot':
            if self.bot_time_left is not None:
                minutes, seconds = divmod(self.bot_time_left, 60)
                self.bot_clock_button.config(text=f"⏰ {minutes:02d}:{seconds:02d}", bg="white" if self.board.turn == chess.BLACK else "gray")
            else:
                self.bot_clock_button.config(text="⏰", bg="red")

    def set_timer(self, player_type):
        # Set the timer for the player or bot
        pass

    def handle_square_click(self, row, col):
        # Handle click event for each square
        if not self.game_started:
            return  # Prevent moves before pressing play button
        selected_square = chess.square(col, 7 - row)
        if self.selected_piece is not None:
            move = chess.Move(self.selected_piece, selected_square)
            if move in self.board.legal_moves:
                self.undo_stack.append(self.board.copy())  # Add current board state to stack
                if self.board.is_capture(move):
                    captured_piece = self.board.piece_at(move.to_square)
                    if self.board.turn == chess.WHITE:
                        self.captured_pieces_bot.append(captured_piece.symbol())
                    else:
                        self.captured_pieces_player.append(captured_piece.symbol())
                self.board.push(move)
                self.selected_piece = None
                self.update_board()
                self.check_end_game()  # Check if game ended after move
                if not self.first_move_played:  # Start timers after the first move is played
                    self.first_move_played = True
                    if self.timed_game:
                        self.root.after(1000, self.start_timers)
                if self.timed_game:
                    self.switch_timer()
                if not self.board.turn and self.game_mode.get() != "freund":
                    self.bot_move()
            else:
                self.selected_piece = None  # Deselect if move is not legal
                self.update_board()  # Remove any highlighted moves
        else:
            piece = self.board.piece_at(selected_square)
            if piece and piece.color == self.board.turn:
                self.selected_piece = selected_square
                self.highlight_moves(selected_square)

    def switch_timer(self):
        # Switch timers between player and bot
        if self.player_timer_running:
            self.player_timer_running = False
            self.start_bot_timer()
        elif self.bot_timer_running:
            self.bot_timer_running = False
            self.start_player_timer()

    def highlight_moves(self, square):
        # Highlight possible moves for the selected piece
        moves = list(self.board.legal_moves)
        for move in moves:
            if move.from_square == square:
                row, col = divmod(move.to_square, 8)
                self.squares[(7 - row, col)].create_oval(35, 35, self.square_size - 35, self.square_size - 35, fill="green", outline="")

    def bot_move(self):
        # Placeholder function for bot move
        result = self.engine.play(self.board, chess.engine.Limit(time=self.bot_time_limit))
        if self.board.is_capture(result.move):
            captured_piece = self.board.piece_at(result.move.to_square)
            self.captured_pieces_player.append(captured_piece.symbol())
        self.board.push(result.move)
        self.update_board()
        self.check_end_game()
        if self.timed_game:
            self.switch_timer()

    def disable_board(self):
        # Disable all squares of the chessboard
        for row in range(8):
            for col in range(8):
                self.squares[(row, col)].unbind("<Button-1>")
                self.squares[(row, col)].configure(bg="gray")

    def enable_board(self):
        # Enable all squares of the chessboard
        for row in range(8):
            for col in range(8):
                self.squares[(row, col)].bind("<Button-1>", lambda event, r=row, c=col: self.handle_square_click(r, c))
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                self.squares[(row, col)].configure(bg=color)

    def check_end_game(self):
        # Check for end game conditions
        if self.board.is_checkmate():
            winner = "Weiß" if self.board.turn == chess.BLACK else "Schwarz"
            reason = "durch Schachmatt"
            self.display_end_game_popup(f"{winner} hat gewonnen!", reason)
        elif self.board.is_stalemate():
            reason = "durch Patt"
            self.display_end_game_popup("Unentschieden", reason)
        elif self.board.is_insufficient_material():
            reason = "aufgrund unzureichendem Material"
            self.display_end_game_popup("Unentschieden", reason)
        elif self.board.is_seventyfive_moves():
            reason = "aufgrund der 75-Züge Regel"
            self.display_end_game_popup("Unentschieden", reason)
        elif self.board.is_fivefold_repetition():
            reason = "durch fünffache Stellungswiederholung"
            self.display_end_game_popup("Unentschieden", reason)
        elif self.board.is_variant_draw():
            reason = "Unentschieden durch spezielle Regel"
            self.display_end_game_popup("Unentschieden", reason)

    def display_end_game_popup(self, result, reason):
        # Ensure only one end game popup is displayed
        if hasattr(self, 'end_game_displayed') and self.end_game_displayed:
            return
        self.end_game_displayed = True

        # Display a popup when the game ends
        end_game_window = tk.Toplevel(self.root)
        end_game_window.title("Spielende")
        end_game_window.configure(bg="white")

        result_label = tk.Label(end_game_window, text=result, font=("Arial", 20, "bold"), fg="black", bg="white")
        result_label.pack(pady=10)

        reason_label = tk.Label(end_game_window, text=reason, font=("Arial", 14), fg="gray", bg="white")
        reason_label.pack(pady=5)

        analyze_button = tk.Button(end_game_window, text="Analysieren", font=("Arial", 16), bg="blue", fg="white", command=self.analyze_game)
        analyze_button.pack(pady=10)

        button_frame = tk.Frame(end_game_window, bg="white")
        button_frame.pack(pady=10)

        new_game_button = tk.Button(button_frame, text="Neues Spiel", font=("Arial", 16), bg="green", fg="white", command=lambda: [self.reset_game(), end_game_window.destroy(), self.clear_end_game_displayed()])
        new_game_button.grid(row=0, column=0, padx=5)

        rematch_button = tk.Button(button_frame, text="Revanche", font=("Arial", 16), bg="orange", fg="white", command=lambda: [self.reset_game(), self.start_game(), end_game_window.destroy(), self.clear_end_game_displayed()])
        rematch_button.grid(row=0, column=1, padx=5)

    def clear_end_game_displayed(self):
        # Reset the end game flag
        self.end_game_displayed = False

    def reset_piece_banks(self):
        # Reset the piece banks
        self.captured_pieces_player.clear()
        self.captured_pieces_bot.clear()
        self.update_piece_banks()

    def analyze_game(self):
        # Placeholder for analyze function
        messagebox.showinfo("Analyse", "Analysefunktion ist noch nicht implementiert.")

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
