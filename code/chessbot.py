# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 14:45:32 2024

@author: Robin Corbonnois
"""


import tkinter as tk  # GUI-Bibliothek für das Erstellen von Benutzeroberflächen
from tkinter import messagebox, scrolledtext, filedialog  # Weitere GUI-Komponenten für Nachrichten, Scrollen und Dateiauswahl
import chess  # Bibliothek für Schachlogik
import chess.engine  # Modul für die Schach-Engine-Interaktion
import os, sys  # Betriebssystem-Operationen und Dateipfade
import threading  # Für Aufgaben im Hintergrund
import comtypes.client  # Schnittstelle für Word-Integration
import webbrowser  # Modul zum Öffnen von URLs im Browser

VERSION = "chessbot platteforme v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup für die ChessApp class
        self.root = root
        self.root.title("Willkommen zu dem BR ChessBot v2")
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="black")
        self.board = chess.Board()
    
        # Brett initialisieren
        self.board = chess.Board()  # Brett auf die Startposition setzen
    
        # Emoji-Zuordnung als Einzelzeile
        self.pieces_emojis = {'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔', 'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'}
    
        # Debugging: Ausgabe aller Figuren auf dem Startbrett
        for square, piece in self.board.piece_map().items():
            piece_symbol = piece.symbol()
            piece_emoji = self.pieces_emojis.get(piece_symbol, '')
            print(f"Square: {chess.square_name(square)}, Piece: {piece}, Symbol: {piece_symbol}, Emoji: {piece_emoji}")
            
        # Spielmodus auf default setzen('einfach' - easy)
        self.game_mode = tk.StringVar(value="einfach")

        # Initialisiere unterschiedliche Spielvariabeln
        self.squares = {}
        self.selected_piece = None
        self.captured_pieces_player = []
        self.captured_pieces_bot = []
        self.piece_values = {
            'p': 1, 'r': 5, 'n': 3, 'b': 3, 'q': 9, 'k': 0,
            'P': 1, 'R': 5, 'N': 3, 'B': 3, 'Q': 9, 'K': 0
        }
        # Emoji-Zuordnung für Schachfiguren
        self.pieces_emojis = {
          'P': '♙',  # Weißer Bauer
          'N': '♘',  # Weißer Springer
          'B': '♗',  # Weißer Läufer
          'R': '♖',  # Weißer Turm
          'Q': '♕',  # Weiße Dame
          'K': '♔',  # Weißer König
          'p': '♟',  # Schwarzer Bauer
          'n': '♞',  # Schwarzer Springer
          'b': '♝',  # Schwarzer Läufer
          'r': '♜',  # Schwarzer Turm
          'q': '♛',  # Schwarze Dame
          'k': '♚'   # Schwarzer König
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
    
    def toggle_sidebar(self):
        if self.sidebar_frame is None:
            # Créer la barre latérale
            self.sidebar_frame = tk.Frame(self.root, width=200, bg="black", relief="sunken", borderwidth=2)
            self.sidebar_frame.place(x=0, y=10, height=self.root.winfo_height())
    
            # Ajouter des boutons dans la barre latérale (enlever "Play")
            tk.Button(self.sidebar_frame, text="Schachregeln", font=("Arial", 18), command=self.open_chess_rules, bg="black", fg="white").pack(pady=10, padx=10, fill=tk.X)
            tk.Button(self.sidebar_frame, text="Dokumentation", font=("Arial", 18), command=self.open_documentation, bg="black", fg="white").pack(pady=10, padx=10, fill=tk.X)
        else:
            # Détruire la barre latérale
            self.sidebar_frame.destroy()
            self.sidebar_frame = None


            
    def show_play_options(self):
        play_options_window = tk.Toplevel(self.root)
        play_options_window.title("Play Options")
        play_options_window.configure(bg="white")
    
        tk.Label(play_options_window, text="Select Play Mode:", font=("Arial", 18), bg="white").pack(pady=10)
        
        # Buttons for different play modes
        tk.Button(play_options_window, text="Easy", font=("Arial", 16), command=lambda: self.set_game_mode("einfach"), bg="green", fg="white").pack(pady=5, padx=20, fill=tk.X)
        tk.Button(play_options_window, text="Medium", font=("Arial", 16), command=lambda: self.set_game_mode("mittel"), bg="orange", fg="white").pack(pady=5, padx=20, fill=tk.X)
        tk.Button(play_options_window, text="Hard", font=("Arial", 16), command=lambda: self.set_game_mode("schwer"), bg="red", fg="white").pack(pady=5, padx=20, fill=tk.X)
        tk.Button(play_options_window, text="Against Friend", font=("Arial", 16), command=lambda: self.set_game_mode("freund"), bg="blue", fg="white").pack(pady=5, padx=20, fill=tk.X)
    
    def open_chess_rules(self):
        webbrowser.open("https://www.chess.com/de/schachregeln")
        
    def open_documentation(self):
        try:
            # Définir le chemin du fichier selon l'environnement (EXE ou script Python)
            if hasattr(sys, '_MEIPASS'):  # Mode EXE (PyInstaller)
                base_path = sys._MEIPASS
            else:  # Mode script Python
                base_path = os.path.abspath(".")
    
            # Construire le chemin absolu vers le fichier
            doc_path = os.path.join(base_path, "chessbot_BR_Schriftliche_Arbeit.docx")
    
            # Vérifier si le fichier existe
            if not os.path.exists(doc_path):
                raise FileNotFoundError(f"Datei nicht gefunden: {doc_path}")
    
            # Ouvrir le fichier avec Microsoft Word
            word = comtypes.client.CreateObject('Word.Application')
            word.Visible = True
            word.Documents.Open(doc_path)
        except FileNotFoundError as fnf_error:
            messagebox.showerror("Fehler", f"Die Dokumentation wurde nicht gefunden: {fnf_error}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
            
    def update_bot_information(self):
        # Get the selected difficulty
        difficulty = self.game_mode.get()
    
        # Set bot parameters based on selected difficulty
        if difficulty == "einfach":
            self.bot_elo = 800
            self.bot_name = "Bot"
        elif difficulty == "mittel":
            self.bot_elo = 1400
            self.bot_name = "Bot"
        elif difficulty == "schwer":
            self.bot_elo = 2000
            self.bot_name = "Bot"
        elif difficulty == "freund":
            self.bot_name = "spieler 2"
            self.bot_elo = 800
            self.bot_photo_label.configure(text="👤")  # Change to player icon
    
        # Update bot information in the GUI
        self.bot_name_label.configure(text=f"{self.bot_name} ({self.bot_elo})")
        self.bot_photo_label.configure(text="🤖" if difficulty != "freund" else "👤")


    def start_game(self):
        # Function to start a game with selected difficulty
        difficulty = self.game_mode.get()
        
        # Deactivate buttons during game
        for child in self.radio_buttons_frame.winfo_children():
            child.configure(state="disabled")
        self.play_button.configure(text="⏸", bg="black", fg="white")
    
        # Check if it's a friend mode, call start_friend_game
        if difficulty == "freund":
            self.start_friend_game()
            return
    
        # Verify if the engine is loaded for the bot game
        if not hasattr(self, 'engine'):
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "\nDie Engine wird noch geladen. Bitte warten Sie einen Moment.")
            self.output_text.configure(state='disabled')
            self.output_text.see(tk.END)
            return
    
        # Update opponent (bot) information for bot mode
        self.bot_name = "Bot"
    
        # Set bot parameters based on selected difficulty
        if difficulty == "einfach":
            self.bot_elo = 800
            self.bot_time_limit = 0.2
            self.bot_depth = 1
        elif difficulty == "mittel":
            self.bot_elo = 1400
            self.bot_time_limit = 0.5
            self.bot_depth = 3
        elif difficulty == "schwer":
            self.bot_elo = 2000
            self.bot_time_limit = 1.0
            self.bot_depth = 6
    
        # Update bot information in the GUI
        self.bot_name_label.configure(text=f"{self.bot_name} ({self.bot_elo})")
        self.bot_photo_label.configure(text="🤖")  # Change icon to bot
    
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
        # Utilisation d'un chemin fixe pour charger Stockfish
        base_path = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False):  # Check if running as a bundled app
            # The application is frozen
            base_path = os.path.dirname(sys.executable)    

        engine_path = os.path.join(base_path, "stockfish", "stockfish-windows-x86-64-avx2.exe")
                
        # Vérification si l'engine est disponible dans le chemin par défaut
        if os.path.isfile(engine_path):
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
                self.output_text.configure(state='normal')
                self.output_text.insert(tk.END, "\nSchach-Engine erfolgreich geladen!")
                self.output_text.configure(state='disabled')
                self.output_text.see(tk.END)
            except Exception as e:
                self.output_text.configure(state='normal')
                self.output_text.insert(tk.END, f"\nFehler beim Laden der Engine: {e}")
                self.output_text.configure(state='disabled')
                self.output_text.see(tk.END)
        else:
            # Message d'erreur si le fichier n'est pas trouvé
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "\nStockfish-Engine nicht gefunden. Bitte installieren Sie den Engine im Ordner stockfish.")
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
                       indicatoron=True, command=self.update_bot_information).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="👴 ", variable=self.game_mode, value="mittel",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_bot_information).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="🏋 ", variable=self.game_mode, value="schwer",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_bot_information).pack(anchor="w", padx=20, pady=5)
    
        tk.Radiobutton(self.radio_buttons_frame, text="👥 ", variable=self.game_mode, value="freund",
                       font=("Arial", 18, "bold"), bg="black", fg="gray",
                       indicatoron=True, command=self.update_bot_information).pack(anchor="w", padx=20, pady=5)
    
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
        
        # Ajoutez l'indicateur d'avantage pour le bot (positioned right after the bot piece bank)
        self.bot_advantage_label = tk.Label(self.top_info_frame, text="", font=("Arial", 16), fg="red", bg="black")
        self.bot_advantage_label.place(x=520, y=50)  # Ajuster x pour être juste derrière la banque de pièces

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
        
        # Ajoutez l'indicateur d'avantage pour le joueur (positioned right after the player piece bank)
        self.player_advantage_label = tk.Label(self.bottom_info_frame, text="", font=("Arial", 16), fg="red", bg="black")
        self.player_advantage_label.place(x=520, y=50)  # Ajuster x pour être juste derrière la banque de pièces

        self.player_photo_label = tk.Label(self.bottom_info_frame, text="👤", font=("Arial", 50), bg="black", fg="white")
        self.player_photo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.player_name_label = tk.Label(self.bottom_info_frame, text=f"{self.player_name} ({self.player_elo})", font=("Arial", 16), fg="white", bg="black")
        self.player_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.player_flag_label = tk.Label(self.bottom_info_frame, text="🇨🇭", font=("Arial", 16), bg="black", fg="white")
        self.player_flag_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.player_clock_button = tk.Label(self.bottom_info_frame, text="⏰", font=("Arial", 16), fg="black", bg="red")
        self.player_clock_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.player_clock_button.bind("<Button-1>", lambda event: self.toggle_clock())
        
        # Ajoutez l'indicateur d'avantage pour le bot
        self.bot_advantage_label = tk.Label(self.top_info_frame, text="", font=("Arial", 16), fg="red", bg="black")
        self.bot_advantage_label.grid(row=0, column=4, padx=5, pady=5, sticky='w')
        
        # Ajoutez l'indicateur d'avantage pour le joueur
        self.player_advantage_label = tk.Label(self.bottom_info_frame, text="", font=("Arial", 16), fg="red", bg="black")
        self.player_advantage_label.grid(row=0, column=4, padx=5, pady=5, sticky='w')



        # Frame for the chessboard
        self.board_frame = tk.Frame(self.general_frame, bg="black")
        self.board_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
    
        # Create chessboard
        self.square_size = 55  # Adjust size accordingly
        for row in range(8):
            for col in range(8):
                square = tk.Canvas(self.board_frame, width=self.square_size, height=self.square_size, highlightthickness=0, bg="gray")
                square.grid(row=row, column=col)
                square.bind("<Button-1>", lambda event, r=row, c=col: self.handle_square_click(r, c))
                self.squares[(row, col)] = square
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                square.create_rectangle(0, 0, self.square_size, self.square_size, outline="black", fill=color)
                if row == 7:
                    square.create_text(self.square_size - 10, self.square_size - 10, text=chr(97 + col), font=("Arial", 12), fill="white")
                if col == 0:
                    square.create_text(10, 10, text=str(8 - row), font=("Arial", 12), fill="white")
    
        # Frame above the output to hold buttons
        self.button_frame = tk.Frame(self.general_frame, bg="black")
        self.button_frame.grid(row=0, column=2, sticky="nsew")
    
        # "Rules 📖" and "Doku 📝" Buttons above output frame
        self.rules_button = tk.Button(self.button_frame, text="📖 Regeln", font=("Arial", 16), bg="black", fg="White", command=self.open_chess_rules,borderwidth=0, relief=tk.FLAT)
        self.rules_button.pack(side=tk.LEFT, padx=10, pady=5)
    
        self.doku_button = tk.Button(self.button_frame, text="📝 Doku", font=("Arial", 16), bg="black", fg="white", command=self.open_documentation,borderwidth=0, relief=tk.FLAT)
        self.doku_button.pack(side=tk.LEFT, padx=10, pady=5)
    
        # Text output frame - reduced size
        self.output_frame = tk.Frame(self.general_frame, bg="black")
        self.output_frame.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
    
        self.output_text = scrolledtext.ScrolledText(self.output_frame, font=("Arial", 12), bg="black", fg="white", wrap=tk.WORD, height=20, width=30)
        self.output_text.pack(expand=True, fill=tk.BOTH)
        self.output_text.insert(tk.END, "Willkommen beim Schachbot! Wählen Sie zuerst einen Spielmodus und klicken Sie auf Spielen, um zu beginnen.")
        self.output_text.configure(state='disabled')
    
        # Add the "Aufgeben / Modus ändern" button - reduced width
        self.abandon_button = tk.Button(self.output_frame, text="Aufgeben / Modus ändern", font=("Arial", 14), command=self.reset_game, bg="blue", fg="white", width=25)
        self.abandon_button.pack(pady=5, fill=tk.X)
    
        self.disable_board()
        self.update_board()


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
                # Löschen Sie alle Figuren und Markierungen, aber behalten Sie die Notationen bei
                square.delete("piece")  # Verwenden Sie eine Tag-basierte Löschung, damit die Notationen erhalten bleiben
                
                # Colorieren Sie die Schachfelder neu
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                square.create_rectangle(0, 0, self.square_size, self.square_size, outline="black", fill=color, tags="square")
    
                # Aktualisieren Sie das Brett mit Figuren
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    symbol = self.pieces[piece.symbol()]
                    square.create_text(self.square_size // 2, self.square_size // 2, text=symbol, font=("Arial", int(self.square_size * 0.5)), anchor="center", tags="piece")
                
                # Zeichnen Sie die Notationen neu, falls es sich um die entsprechende Reihe oder Spalte handelt
                if row == 7:  # Unten stehende Spaltenbezeichnungen (Buchstaben)
                    square.create_text(self.square_size - 10, self.square_size - 10, text=chr(97 + col), font=("Arial", 12), fill="white", tags="notation")
                if col == 0:  # Links stehende Zeilenbezeichnungen (Zahlen)
                    square.create_text(10, 10, text=str(8 - row), font=("Arial", 12), fill="white", tags="notation")
    
        if self.board.is_check():
            # Markieren Sie das bedrohte Königsfeld, wenn Schach vorliegt
            king_square = self.board.king(self.board.turn)
            row, col = divmod(king_square, 8)
            self.squares[(7 - row, col)].create_rectangle(0, 0, self.square_size, self.square_size, outline="red", width=5, tags="check")
    
        # Update the piece banks (captured pieces)
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
        # Calculer l'avantage des pièces capturées
        player_advantage = sum(self.piece_values[piece] for piece in self.captured_pieces_bot)
        bot_advantage = sum(self.piece_values[piece] for piece in self.captured_pieces_player)
    
        advantage = player_advantage - bot_advantage
    
        # Mettre à jour l'indicateur d'avantage pour le joueur et le bot
        if advantage > 0:
            self.player_advantage_label.configure(text=f"+{advantage}")
            self.bot_advantage_label.configure(text="")
        elif advantage < 0:
            self.bot_advantage_label.configure(text=f"+{-advantage}")
            self.player_advantage_label.configure(text="")
        else:
            self.player_advantage_label.configure(text="")
            self.bot_advantage_label.configure(text="")
        
        # Forcer la mise à jour de l'affichage pour s'assurer que les changements sont visibles
        self.root.update_idletasks()

  
    def reset_game(self):
        # Fonction pour réinitialiser le jeu
        self.board.reset()
        self.reset_piece_banks()
        self.update_board()
        self.disable_board()  # Désactivez l'échiquier
        
        # Réinitialiser toutes les variables liées à l'état du jeu
        self.selected_piece = None
        self.undo_stack = []
        self.game_started = False
        self.first_move_played = False
        self.player_timer_running = False
        self.bot_timer_running = False
        
        # Réinitialiser l'état des horloges
        self.timed_game = False
        self.timed_button_active = False
        self.player_time_left = None
        self.bot_time_left = None
        
        # Conserver le mode de jeu sélectionné (ne pas réinitialiser game_mode)
        current_mode = self.game_mode.get()
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, f"\nDas Spiel wurde reinitialisiert. Aktueller Modus: {current_mode}")
        self.output_text.configure(state='disabled')
        
        # Mettre à jour les étiquettes (exemple : changer l'icône du bot à l'icône de joueur)
        if current_mode == "freund":
            self.bot_name = "Spieler 2"
            self.bot_elo = 800
            self.bot_photo_label.configure(text="👤")
        else:
            self.bot_name = "Bot"
            self.bot_elo = 1200
            self.bot_photo_label.configure(text="🤖")
        
        self.bot_name_label.configure(text=f"{self.bot_name} ({self.bot_elo})")
        self.bot_flag_label.configure(text="🇨🇭")
        self.player_flag_label.configure(text="🇨🇭")
        
        # Réinitialiser les boutons d'horloge
        self.bot_clock_button.config(bg="red", text="⏰")
        self.player_clock_button.config(bg="red", text="⏰")
        
        # Réactiver les boutons radio pour choisir le mode de jeu
        for child in self.radio_buttons_frame.winfo_children():
            child.configure(state="normal")
        
        # Réactiver le bouton Play
        self.play_button.configure(state="normal", text="▶ ", bg="green", fg="white")
        
        # Mise à jour de l'interface
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
         print(f"[DEBUG] Clicked on square: row={row}, col={col}, selected_square={selected_square}")  # Debugging
     
         if self.selected_piece is not None:
             # Player is moving a piece already selected
             move = chess.Move(self.selected_piece, selected_square)
             piece = self.board.piece_at(self.selected_piece)
     
             # Check if the move is a promotion move
             if piece and piece.piece_type == chess.PAWN:
                 print(f"[DEBUG] Selected piece is a pawn at square {self.selected_piece}")
                 if chess.square_rank(selected_square) == 0 or chess.square_rank(selected_square) == 7:
                     # Pawn is reaching promotion rank - set a default promotion to queen for legality check
                     move = chess.Move(self.selected_piece, selected_square, promotion=chess.QUEEN)
                     print(f"[DEBUG] Pawn promotion detected. Promotion move: {move}")
     
             # Check if the move is legal
             if move in self.board.legal_moves:
                 self.undo_stack.append(self.board.copy())  # Save the current state for undo
     
                 # Handle pawn promotion window if needed
                 if piece and piece.piece_type == chess.PAWN and (
                         chess.square_rank(selected_square) == 0 or chess.square_rank(selected_square) == 7):
                     # Open the promotion window to choose a piece
                     print(f"[DEBUG] Legal pawn promotion move to {selected_square}. Opening promotion window.")
                     self.open_promotion_window(move)
                     return
     
                 # Push the move normally if not a promotion
                 self.push_move(move)
     
                 # Switch the timer if it's a timed game
                 if self.timed_game:
                     self.switch_timer()
     
                 # If playing against the bot, make the bot move
                 if not self.board.turn and self.game_mode.get() != "freund":
                     self.bot_move()
             else:
                 # Invalid move: deselect the piece and update the display
                 print(f"[DEBUG] Move from {self.selected_piece} to {selected_square} is not legal.")
                 self.selected_piece = None
                 self.update_board()
         else:
             # No piece is selected, check if the square contains a piece of the current player
             piece = self.board.piece_at(selected_square)
             if piece and piece.color == self.board.turn:
                 self.selected_piece = selected_square
                 print(f"[DEBUG] Selected a piece at {selected_square}")
                 self.highlight_moves(selected_square)  # Highlight possible moves for the selected piece
             else:
                 print(f"[DEBUG] No valid piece to select at {selected_square}")

    def open_promotion_window(self, move):
        # Speichern Sie den Zug, damit er in promote_to verwendet werden kann
        self.move_to_promote = move
    
        # Erstellen Sie das Promotionsfenster als vertikales Menü
        promotion_window = tk.Toplevel(self.root)
        promotion_window.title("Promotion")
    
        # Bestimmen Sie die Farbe des Fensters basierend auf der Farbe des Bauern
        piece_color = self.board.piece_at(move.from_square).color
        if piece_color == chess.WHITE:
            bg_color = "Black"
            fg_color = "white"
        else:
            bg_color = "white"
            fg_color = "black"
    
        promotion_window.configure(bg=bg_color)
    
        # Koordinaten des Zielfeldes (to_square) abrufen
        target_square = move.to_square
        row, col = divmod(target_square, 8)
        square_widget = self.squares[(7 - row, col)]
    
        # Absolute Koordinaten des Feldes auf dem Bildschirm erhalten
        square_x = square_widget.winfo_rootx()
        square_y = square_widget.winfo_rooty()
        square_width = square_widget.winfo_width()
        square_height = square_widget.winfo_height()
    
        # Das Promotionsfenster so positionieren, dass es zentriert über der Schachfeld liegt
        window_width = square_width
        window_height = square_height * 4  # Für die 4 Promotionsoptionen
    
        # Berechnen Sie die Position basierend auf der Farbe des Bauern
        if piece_color == chess.WHITE:
            # Für weiße Bauern, Fenster leicht nach unten verschieben
            y_offset = square_y - window_height + square_height // 2 + 350  # +30 schiebt das Fenster etwas nach unten
        else:
            # Für schwarze Bauern, Fenster leicht nach oben schieben
            y_offset = square_y - window_height + square_height // 2 + 20  # 20 schiebt das Fenster nach oben
    
        x_offset = square_x
    
        # Definieren Sie die Größe und Position des Promotionsfensters
        promotion_window.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")
        promotion_window.transient(self.root)
        promotion_window.grab_set()  # Machen Sie das Fenster modaler
    
        # Erstellen Sie die Buttons für die Promotion
        options_frame = tk.Frame(promotion_window, bg=bg_color)
        options_frame.pack(expand=True, fill=tk.BOTH)
    
        # Funktion promote_to definieren, um den Promotion-Typ festzulegen und den Zug durchzuführen
        def promote_to(piece_type):
            self.move_to_promote.promotion = piece_type
            self.push_move(self.move_to_promote)
            promotion_window.destroy()
    
        # Fügen Sie die Buttons für die Promotion hinzu, jetzt mit den entsprechenden Emojis
        pieces = [
            (chess.QUEEN, "♛"),  # Königin
            (chess.KNIGHT, "♞"),  # Springer
            (chess.ROOK, "♜"),    # Turm
            (chess.BISHOP, "♝")   # Läufer
        ]
    
        for piece, emoji in pieces:
            button = tk.Button(options_frame, text=emoji, font=("Arial", 24),
                               command=lambda p=piece: promote_to(p),
                               bg=bg_color, fg=fg_color, borderwidth=0)
            button.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=1)


    def push_move(self, move):
        # Récupérer la pièce à la case de départ AVANT d'exécuter le coup
        from_piece = self.board.piece_at(move.from_square)
    
        # Vérifier s'il s'agit d'une capture et enregistrer la pièce capturée
        if self.board.is_capture(move):
            captured_piece = self.board.piece_at(move.to_square)
            if captured_piece is not None:
                print(f"[INFO] Capture détectée : {captured_piece.symbol()} sur la case {chess.square_name(move.to_square)}")
                if self.board.turn == chess.WHITE:
                    # Si c'est au tour des Blancs, alors la pièce capturée est celle des Noirs
                    self.captured_pieces_bot.append(captured_piece.symbol())
                else:
                    # Si c'est au tour des Noirs, alors la pièce capturée est celle des Blancs
                    self.captured_pieces_player.append(captured_piece.symbol())
    
        # Exécuter le coup sur le plateau
        self.board.push(move)  # Mettre à jour l'état du plateau
    
        # Afficher le coup dans la sortie, en passant la pièce d'origine
        self.display_move_in_output(move, from_piece)
        
        # Mettre à jour la représentation graphique du plateau
        self.update_board()
        
        # Mettre à jour l'avantage des pièces capturées après le coup
        self.update_advantage()
    
        # Vérifier si la partie est terminée
        self.check_end_game()
        
        # Start timers on the first move if it's a timed game
        if not self.first_move_played:
            self.first_move_played = True
            if self.timed_game:
                self.root.after(1000, self.start_timers)


    def make_move(self, move):
        # Aktualisiere das Brett mit dem neuen Zug
        self.board.push(move)
        # Dann die Anzeige des Zuges aktualisieren
        self.display_move_in_output(move)

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

    def display_move_in_output(self, move, from_piece=None):
        # Ajouter deux lignes vides seulement au début de l'affichage des mouvements
        if len(self.board.move_stack) == 1:
            # Si c'est le premier mouvement, ajoute deux lignes vides pour espacer
            self.output_text.configure(state='normal')
            self.output_text.insert(tk.END, "\n\n")
            self.output_text.configure(state='disabled')
            
        # Déterminer l'emoji de la pièce déplacée
        piece_emoji = ''
        if from_piece:
            piece_symbol = from_piece.symbol()
            piece_emoji = self.pieces_emojis.get(piece_symbol, '')
    
        # Déterminer la case cible
        target_square = chess.square_name(move.to_square)
    
        # Construire la représentation du mouvement
        display_move = f"{piece_emoji}{target_square}"
    
        # Gestion des cas spéciaux : roque, promotion, prise en passant
        if from_piece and from_piece.piece_type == chess.KING:
            if move.from_square == chess.E1 and move.to_square == chess.G1:
                display_move = "0-0"
            elif move.from_square == chess.E1 and move.to_square == chess.C1:
                display_move = "0-0-0"
            elif move.from_square == chess.E8 and move.to_square == chess.G8:
                display_move = "0-0"
            elif move.from_square == chess.E8 and move.to_square == chess.C8:
                display_move = "0-0-0"
        elif from_piece and from_piece.piece_type == chess.PAWN:
            if move.promotion:
                promotion_piece = chess.Piece(move.promotion, from_piece.color)
                promotion_emoji = self.pieces_emojis.get(promotion_piece.symbol(), '')
                display_move = f"{piece_emoji}{target_square}={promotion_emoji}"
            elif self.board.is_en_passant(move):
                display_move = f"{piece_emoji}{target_square}!"
    
        # Ajouter notation pour échec ou mat
        if self.board.is_checkmate():
            display_move += '#'
        elif self.board.is_check():
            display_move += '+'
    
        # Déterminer si c'est le tour des Blancs ou des Noirs
        move_number = (len(self.board.move_stack) + 1) // 2
        if self.board.turn == chess.BLACK:
            # Ajout du numéro de coup pour les Blancs seulement
            formatted_move = f"{move_number}. {display_move} "
        else:
            # Ne pas répéter le numéro de coup pour les Noirs
            formatted_move = f"{display_move}\n"
    
        # Ajouter le coup dans le champ de texte
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, formatted_move)
        self.output_text.configure(state='disabled')
        self.output_text.see(tk.END)


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
