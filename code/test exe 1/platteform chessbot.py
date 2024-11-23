
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 18:11:38 2024

@author: Robin Corbonnois
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import chess
import chess.engine
import os
import threading  # Import threading for running tasks in background

VERSION = "chessbot platteforme v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Willkommen zu dem BR ChessBot v2")
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="black")
        self.board = chess.Board()

        # Set game mode to default ('einfach' - easy)
        self.game_mode = tk.StringVar(value="einfach")

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
        self.pawn_color = tk.StringVar(value="white")  # Track pawn color selection

        # Create the user interface for the game
        self.create_game_interface()

        # Charger l'engine Stockfish dans un thread séparé pour éviter de bloquer l'interface
        self.engine_thread = threading.Thread(target=self.load_engine, daemon=True)
        self.engine_thread.start()

    def start_game(self):
        # Function to start a game with selected difficulty
        difficulty = self.game_mode.get()

        #Desactivate button during game
        for child in self.radio_buttons_frame.winfo_children():
            child.configure(state="disabled")
        self.play_button.configure(text="⏸", bg="black", fg="white")

        # Check if it's a friend mode, call start_friend_game
        if difficulty == "freund":
            self.start_friend_game()
            return

        # Vérifier si l'engine est chargé pour le jeu contre le bot
        if not hasattr(self, 'engine'):
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "\nDie Engine wird noch geladen. Bitte warten Sie einen Moment.")
            self.output_text.configure(state='disabled')
            self.output_text.see(tk.END)
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

    def load_engine(self):
        # Demander le chemin vers l'engine dans le thread principal (pour éviter les problèmes liés à l'interface)
        engine_path = self.browse_for_engine()

        if not engine_path:
            # Aucun chemin sélectionné, terminer le programme proprement
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "\nKein Pfad zur Engine ausgewählt. Bot-Modus nicht verfügbar.")
            self.output_text.configure(state='disabled')
            self.output_text.see(tk.END)
            return

        try:
            # Charger l'engine Stockfish
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            # Insérer une notification dans le texte déroulant (output_text) à la place d'un pop-up
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "\nSchach-Engine erfolgreich geladen!")  # Notify when engine is ready
            self.output_text.configure(state='disabled')
            self.output_text.see(tk.END)  # Scroll to the bottom to show the latest message
        except Exception as e:
            # Afficher l'erreur dans l'output_text au lieu d'une boîte de message
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, f"\nFehler beim Laden der Engine: {e}")
            self.output_text.configure(state='disabled')
            self.output_text.see(tk.END)

    def browse_for_engine(self):
        # Function to prompt user to browse for the Stockfish engine
        return filedialog.askopenfilename(
            title="Select Stockfish Engine",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )

  
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
    
        # Create a container frame to hold the title, control frame, and quit button
        self.container_frame = tk.Frame(self.general_frame, bg="black")
        self.container_frame.grid(row=1, column=0, sticky="", pady=20)  # Center vertically in the left column
    
        # Add "Chessbot Br" text at the top of the container frame
        self.title_label = tk.Label(self.container_frame, text="Chessbot Br", font=("Comic Sans MS", 24, "bold"), bg="black", fg="white")
        self.title_label.pack(pady=10)
    
        # Create a control frame for Play button and Radio buttons
        self.control_frame = tk.Frame(self.container_frame, bg="black", bd=3, relief="groove")
        self.control_frame.pack(pady=20)  # Add some space around the control frame
    
        # Configure grid layout within control_frame to align Play button and Radio buttons
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)
    
        # Play Button, placed in control_frame
        self.play_button = tk.Button(self.control_frame, text="▶ ", font=("Arial", 20), bg="green", fg="white", command=self.start_game, width=5)
        self.play_button.grid(row=0, column=0, padx=10, pady=10)
    
        # Frame for radio buttons, also inside control_frame
        self.radio_buttons_frame = tk.Frame(self.control_frame, bg="black")
        self.radio_buttons_frame.grid(row=0, column=1, padx=0, pady=10)
    
        # Creating Radio buttons for different game modes
        tk.Radiobutton(self.radio_buttons_frame, text="👼 ", variable=self.game_mode, value="einfach",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="👴 ", variable=self.game_mode, value="mittel",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="🏋 ", variable=self.game_mode, value="schwer",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="👥 ", variable=self.game_mode, value="freund",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_selected_mode_display).pack(anchor="w", padx=20, pady=5)
    
        # Quit Button - Placed at the bottom of container_frame, centered
        self.quit_button = tk.Button(self.container_frame, text="⛔ Beenden", font=("Arial", 20), bg="red", fg="white", command=self.on_closing, width=10)
        self.quit_button.pack(pady=(20, 0))



        # Update the GUI to ensure all elements are displayed correctly
        self.root.update()
    
        # Timed game toggle button (removed and replaced with clock label activation)
        self.timed_button_active = False
    
        # Top information frame for bot details (swapped position)
        self.top_info_frame = tk.Frame(self.general_frame, bg="black")
        self.top_info_frame.grid(row=0, column=1, sticky="nsew")
    
        # Bot piece bank (placed behind bot info)
        self.bot_bank_frame = tk.Frame(self.top_info_frame, bg="black")
        self.bot_bank_frame.place(x=110, y=50)
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
                # Dessiner les cases de l'échiquier
                square = tk.Canvas(self.board_frame, width=self.square_size, height=self.square_size, highlightthickness=0, bg="gray")
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.handle_square_click(r, c))
                self.squares[(row, col)] = square
        
                # Colorier les cases
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                square.create_rectangle(0, 0, self.square_size, self.square_size, outline="black", fill=color)
        
                # Annoter l'échiquier avec les lettres et les chiffres
                if row == 7:  # Bottom row for columns (letters)
                    square.create_text(self.square_size - 10, self.square_size - 10, text=chr(97 + col), font=("Arial", 12), fill="white")  # Utiliser une couleur contrastante
                if col == 0:  # Left column for rows (numbers)
                    square.create_text(10, 10, text=str(8 - row), font=("Arial", 12), fill="white")  # Utiliser une couleur contrastante

        # Frame for move history or bot output
        self.output_frame = tk.Frame(self.general_frame, bg="black")
        self.output_frame.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(self.output_frame, width=30, height=40, font=("Arial", 12), bg="black", fg="white", wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "Willkommen beim Schachbot! Wählen Sie zuerst einen Spielmodus und klicken Sie auf Spielen, um zu beginnen.")
        self.output_text.configure(state='disabled')
    
        # Add the "Aufgeben" button to allow changing the mode after starting the game
        self.abandon_button = tk.Button(self.output_frame, text="Aufgeben / Modus ändern", font=("Arial", 16), command=self.reset_game, bg="blue", fg="white")
        self.abandon_button.pack(pady=5, fill=tk.X)
    
        self.disable_board()
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
        
        #reset when pressed aufgeben
        for child in self.radio_buttons_frame.winfo_children():
            child.configure(state="normal")

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
    
        selected_square = chess.square(col, 7 - row)  # Convert the clicked square to internal notation
        if self.selected_piece is not None:
            move = chess.Move(self.selected_piece, selected_square)
    
            # Check if the move is legal
            if move in self.board.legal_moves:
                self.undo_stack.append(self.board.copy())  # Save the current state for undo
    
                # Handle pawn promotion
                piece = self.board.piece_at(self.selected_piece)
                if piece and piece.piece_type == chess.PAWN and (
                        chess.square_rank(selected_square) == 0 or chess.square_rank(selected_square) == 7):
                    # Open promotion window
                    self.open_promotion_window(move)
                else:
                    # Push the move normally
                    self.push_move(move)
    
                # Switch the timer if it's a timed game
                if self.timed_game:
                    self.switch_timer()
    
                # If playing against the bot, make the bot move
                if not self.board.turn and self.game_mode.get() != "freund":
                    self.bot_move()
            else:
                # Invalid move: deselect the piece and update the display
                self.selected_piece = None
                self.update_board()
        else:
            # If no piece is selected, check if the square contains a piece of the current player
            piece = self.board.piece_at(selected_square)
            if piece and piece.color == self.board.turn:
                self.selected_piece = selected_square
                self.highlight_moves(selected_square)  # Highlight possible moves for the selected piece

    def open_promotion_window(self, move):
        # Window to select promotion piece
        promotion_window = tk.Toplevel(self.root)
        promotion_window.title("Promotion")
        promotion_window.geometry("250x150")
        promotion_window.configure(bg="black")
        promotion_window.transient(self.root)
        promotion_window.grab_set()  # Make the promotion window modal
    
        label = tk.Label(promotion_window, text="Choose promotion piece:", font=("Arial", 14), fg="white", bg="black")
        label.pack(pady=10)
    
        options_frame = tk.Frame(promotion_window, bg="black")
        options_frame.pack()
    
        def promote_to(piece_type):
            # Set the move promotion
            move.promotion = piece_type
            self.push_move(move)  # Push the move after selecting the promotion piece
            promotion_window.destroy()
    
        # Add buttons for each piece type
        pieces = [(chess.QUEEN, "Queen"), (chess.ROOK, "Rook"), (chess.BISHOP, "Bishop"), (chess.KNIGHT, "Knight")]
        for piece, label_text in pieces:
            button = tk.Button(options_frame, text=label_text, font=("Arial", 14), command=lambda p=piece: promote_to(p))
            button.pack(side=tk.LEFT, padx=5)

    def push_move(self, move):
        # Execute the move on the board
        if self.board.is_capture(move):
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece is not None:
                if self.board.turn == chess.WHITE:
                    self.captured_pieces_bot.append(captured_piece.symbol())
                else:
                    self.captured_pieces_player.append(captured_piece.symbol())
    
        # Push the move
        self.board.push(move)
        self.display_move_in_output(move)  # Display the move in output
        self.update_board()  # Update the graphical representation of the board
        self.check_end_game()  # Check if the game is over
    
        # Start timers on the first move if it's a timed game
        if not self.first_move_played:
            self.first_move_played = True
            if self.timed_game:
                self.root.after(1000, self.start_timers)

    def display_move_in_output(self, move):
        # Ajouter deux lignes vides seulement au début de l'affichage des mouvements
        if len(self.board.move_stack) == 1:
            # Si c'est le premier mouvement, ajoute deux lignes vides pour espacer
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "\n\n")
            self.output_text.configure(state='disabled')
    
        # Déterminer la pièce en mouvement
        from_piece = self.board.piece_at(move.from_square)
        piece_emoji = self.pieces_emojis.get(from_piece.symbol(), '') if from_piece else ''
        
        # Convertir le mouvement au format d'affichage
        display_move = f"{move.uci()[2:]}"
    
       # Vérifier les cas spéciaux comme le roque, l'échec et le mat
       # Vérifier les cas spéciaux comme le roque, l'échec et le mat
        if from_piece and from_piece.piece_type == chess.KING:
          # Roque court ou long, pour blanc et noir
          if (move.from_square == chess.E1 and move.to_square == chess.G1) or (move.from_square == chess.E8 and move.to_square == chess.G8):
              display_move = "0-0"  # Roque court
          elif (move.from_square == chess.E1 and move.to_square == chess.C1) or (move.from_square == chess.E8 and move.to_square == chess.C8):
              display_move = "0-0-0"  # Roque long

        elif self.board.is_checkmate():
             display_move += '#'
        elif self.board.is_check():
             display_move += '+'
    
        # Déterminer le numéro du mouvement et s'il s'agit du tour des blancs ou des noirs
        move_number = (len(self.board.move_stack) + 1) // 2
        if len(self.board.move_stack) % 2 == 1:
            # Mouvement des blancs
            formatted_move = f"{move_number}. {piece_emoji} {display_move}  "
        else:
            # Mouvement des noirs sur la même ligne
            formatted_move = f"{piece_emoji} {display_move}\n"
    
        # Ajouter le mouvement dans la zone de texte de sortie
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, formatted_move)
        self.output_text.configure(state='disabled')
        self.output_text.see(tk.END)

         
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
        # Let the bot make a move using the engine
        result = self.engine.play(self.board, chess.engine.Limit(time=self.bot_time_limit))
    
        # Handle bot promotion (automatically promote to Queen)
        if self.board.piece_at(result.move.from_square).piece_type == chess.PAWN and (
                chess.square_rank(result.move.to_square) == 0 or chess.square_rank(result.move.to_square) == 7):
            result.move = chess.Move(result.move.from_square, result.move.to_square, promotion=chess.QUEEN)
    
        # Handle capture
        if self.board.is_capture(result.move):
            captured_piece = self.board.piece_at(result.move.to_square)
            if captured_piece is not None:
                self.captured_pieces_player.append(captured_piece.symbol())
    
        # Push the move
        self.board.push(result.move)
        self.update_board()
        self.display_move_in_output(result.move)  # Display bot's move
        self.check_end_game()
    
        # Switch timer if timed game
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