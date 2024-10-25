# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 15:36:49 2024

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
        
        self.pieces_emojis = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }

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
    
        # Game mode selection frame (Radio buttons and Play button together)
        self.mode_frame = tk.Frame(self.general_frame, bg="black")
        self.mode_frame.grid(row=1, column=0, sticky="", padx=20, pady=(10, 10))
    
        # Description label centered at the top of the mode frame
        self.description_label = tk.Label(self.mode_frame, text="Chessbot Br", font=("Comic Sans MS", 24, "bold"), bg="black", fg="white")
        self.description_label.pack(side="top", anchor="center", expand=True, padx=20, pady=(5, 5))
    
        # Container frame for the radio buttons and play button with green border
        self.radio_and_play_container = tk.Frame(self.mode_frame, bg="white", bd=4, relief="solid")
        self.radio_and_play_container.pack(side="top", anchor="center", pady=(0, 5))
    
        # Inner frame inside the green border for better alignment
        self.radio_and_play_frame = tk.Frame(self.radio_and_play_container, bg="black")
        self.radio_and_play_frame.pack(padx=5, pady=5)
    
        # Play Button, positioned in the leftmost column of the frame
        self.play_button = tk.Button(self.radio_and_play_frame, text="▶", font=("Arial", 30), bg="green", fg="white", command=self.start_game, width=5)
        self.play_button.grid(row=0, column=0, rowspan=4, padx=(0, 20))
    
        # Creating Radio buttons for different game modes, positioned to the right of the Play button
        tk.Radiobutton(self.radio_and_play_frame, text="👼 Einfach", variable=self.game_mode, value="einfach",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).grid(row=0, column=1, sticky="w", padx=10, pady=(0, 0))
    
        tk.Radiobutton(self.radio_and_play_frame, text="👴 Mittel", variable=self.game_mode, value="mittel",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).grid(row=1, column=1, sticky="w", padx=10, pady=(0, 0))
    
        tk.Radiobutton(self.radio_and_play_frame, text="🏋 Schwer", variable=self.game_mode, value="schwer",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).grid(row=2, column=1, sticky="w", padx=10, pady=(0, 0))
    
        tk.Radiobutton(self.radio_and_play_frame, text="👥 Freund", variable=self.game_mode, value="freund",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).grid(row=3, column=1, sticky="w", padx=10, pady=(0, 0))
    
        # Use 'place' to precisely position the Quit Button ("Beenden")
        self.quit_button = tk.Button(self.root, text="❌ Beenden", font=("Arial", 20), bg="red", fg="white", command=self.on_closing, width=10)
        self.quit_button.place(x=375, y=850)
    
        # Frame for the chessboard
        self.board_frame = tk.Frame(self.general_frame, bg="black")
        self.board_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
    
        # Create chessboard
        self.square_size = 100
        self.squares = {}  # Make sure to initialize the squares dictionary
        for row in range(8):
            for col in range(8):
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                square = tk.Canvas(self.board_frame, width=self.square_size, height=self.square_size, highlightthickness=0, bg=color)
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.handle_square_click(r, c))
                self.squares[(row, col)] = square
    
        # Top information frame for bot details
        self.top_info_frame = tk.Frame(self.general_frame, bg="black")
        self.top_info_frame.grid(row=0, column=1, sticky="nsew")
    
        self.bot_photo_label = tk.Label(self.top_info_frame, text="🤖", font=("Arial", 50), bg="black", fg="white")
        self.bot_photo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.bot_name_label = tk.Label(self.top_info_frame, text=f"{self.bot_name} ({self.bot_elo})", font=("Arial", 16), fg="white", bg="black")
        self.bot_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.bot_flag_label = tk.Label(self.top_info_frame, text="🇨🇭", font=("Arial", 16), bg="black", fg="white")
        self.bot_flag_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
    
        # Player information frame
        self.bottom_info_frame = tk.Frame(self.general_frame, bg="black")
        self.bottom_info_frame.grid(row=2, column=1, sticky="nsew")
    
        self.player_photo_label = tk.Label(self.bottom_info_frame, text="👤", font=("Arial", 50), bg="black", fg="white")
        self.player_photo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.player_name_label = tk.Label(self.bottom_info_frame, text=f"{self.player_name} ({self.player_elo})", font=("Arial", 16), fg="white", bg="black")
        self.player_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.player_flag_label = tk.Label(self.bottom_info_frame, text="🇨🇭", font=("Arial", 16), bg="black", fg="white")
        self.player_flag_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
    
        # Frame for move history or bot output
        self.output_frame = tk.Frame(self.general_frame, bg="black")
        self.output_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        self.output_text = tk.scrolledtext.ScrolledText(self.output_frame, width=30, height=40, font=("Arial", 12), bg="black", fg="white", wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Willkommen beim Schachbot! Wählen Sie zuerst einen Spielmodus und klicken Sie auf Spielen, um zu beginnen.")
        self.output_text.configure(state='disabled')
    
        # Add the "Aufgeben" button to allow changing the mode after starting the game
        self.abandon_button = tk.Button(self.output_frame, text="Aufgeben / Modus ändern", font=("Arial", 16), command=self.reset_game, bg="blue", fg="white")
        self.abandon_button.pack(pady=5, fill=tk.X)
    
        # Update the GUI to ensure all elements are displayed correctly
        self.root.update()

    
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
    
        selected_square = chess.square(col, 7 - row)  # Convert selected square to internal notation
        if self.selected_piece is not None:
            # Create the move from selected piece and destination
            move = chess.Move(self.selected_piece, selected_square)
    
            piece = self.board.piece_at(self.selected_piece)
    
            # Check if it's a legal move
            if move in self.board.legal_moves:
                # Check if it's a pawn promotion
                if piece.piece_type == chess.PAWN:
                    if (piece.color == chess.WHITE and chess.square_rank(self.selected_piece) == 6) or \
                       (piece.color == chess.BLACK and chess.square_rank(self.selected_piece) == 1):
                        # The pawn is on the penultimate rank, and its next move can be a promotion
                        if chess.square_rank(selected_square) == 7 or chess.square_rank(selected_square) == 0:
                            # Call the function to prompt the user for pawn promotion
                            self.prompt_pawn_promotion(move)
                            self.selected_piece = None
                            return
    
                # Check if the move is en passant
                if piece.piece_type == chess.PAWN and self.board.is_en_passant(move):
                    captured_square = move.to_square + (-8 if self.board.turn == chess.WHITE else 8)
                    captured_piece = self.board.piece_at(captured_square)
                    if captured_piece:
                        if self.board.turn == chess.WHITE:
                            self.captured_pieces_bot.append(captured_piece.symbol())
                        else:
                            self.captured_pieces_player.append(captured_piece.symbol())
    
                # Otherwise, execute the move normally
                self.execute_move(move)
    
                # Reset selected piece after move
                self.selected_piece = None
            else:
                # Illegal move: deselect the piece and update display
                self.selected_piece = None
                self.update_board()
        else:
            # If no piece is selected, check if the square contains a piece for the current player
            piece = self.board.piece_at(selected_square)
            if piece and piece.color == self.board.turn:
                self.selected_piece = selected_square
                self.highlight_moves(selected_square)  # Highlight possible moves for the selected piece
            def prompt_pawn_promotion(self, move):
                # Create a popup window for the promotion
                promotion_window = tk.Toplevel(self.root)
                promotion_window.title("Pawn Promotion")
                promotion_window.configure(bg="black")
                promotion_window.geometry("300x200")
            
                label = tk.Label(promotion_window, text="Choose a piece to promote to:", font=("Arial", 14), fg="white", bg="black")
                label.pack(pady=10)
            
                # Function to promote based on selection
                def promote_to(piece_type):
                    promotion_move = chess.Move(move.from_square, move.to_square, promotion=piece_type)
                    if promotion_move in self.board.legal_moves:
                        self.execute_move(promotion_move)  # Correctly execute promotion
                    else:
                        messagebox.showerror("Error", "Invalid promotion move.")
                    promotion_window.destroy()
            
                # Add buttons for each promotion piece
                button_font = ("Arial", 12)
                tk.Button(promotion_window, text="♛ Queen", font=button_font, command=lambda: promote_to(chess.QUEEN)).pack(pady=5)
                tk.Button(promotion_window, text="♜ Rook", font=button_font, command=lambda: promote_to(chess.ROOK)).pack(pady=5)
                tk.Button(promotion_window, text="♝ Bishop", font=button_font, command=lambda: promote_to(chess.BISHOP)).pack(pady=5)
                tk.Button(promotion_window, text="♞ Knight", font=button_font, command=lambda: promote_to(chess.KNIGHT)).pack(pady=5)

          

    def execute_move(self, move):
        # Save the current board state for undo
        self.undo_stack.append(self.board.copy())
    
        # Handle piece capture if applicable
        if self.board.is_capture(move):
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece is not None:
                if self.board.turn == chess.WHITE:
                    self.captured_pieces_bot.append(captured_piece.symbol())
                else:
                    self.captured_pieces_player.append(captured_piece.symbol())
    
        # Apply the move to the board
        self.board.push(move)
        self.display_move_in_output(move)  # Display the move in SAN notation
        self.update_board()  # Update the graphical representation of the board
        self.check_end_game()  # Check if the game is over after this move
    
        # Start timers if it's the first action
        if not self.first_move_played:
            self.first_move_played = True
            if self.timed_game:
                self.root.after(1000, self.start_timers)
    
        # Switch timers if the game is timed
        if self.timed_game:
            self.switch_timer()
    
        # Make the bot move if playing against the bot
        if not self.board.turn and self.game_mode.get() != "freund":
            self.bot_move()

           
    def display_move_in_output(self, move):
        # Convertir le mouvement en notation UCI
        move_uci = move.uci()
    
        # Ajouter le mouvement à la zone de texte
        self.output_text.configure(state='normal')  # Déverrouiller la zone de texte
        self.output_text.insert(tk.END, f"\n{move_uci}")  # Ajouter le mouvement en notation UCI
        self.output_text.configure(state='disabled')  # Verrouiller la zone de texte
        self.output_text.see(tk.END)  # Faire défiler vers le bas pour voir le dernier mouvement ajouté



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
        self.display_move_in_output(result.move)  # Display bot's move
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
