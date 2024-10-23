import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

VERSION = "chessbot v2"

class ChessApp:
    def __init__(self, root):
        # Initial setup for the ChessApp class
        self.root = root
        self.root.title("Schachspiel")
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="black")

        # Create initial interface
        self.create_initial_interface()

    def create_initial_interface(self):
        # Clear the screen
        self.clear_screen()

        # General frame that holds everything, helps centralize components
        self.general_frame = tk.Frame(self.root, bg="black")
        self.general_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)

        # Configure a 2x2 grid layout that takes the entire screen
        self.general_frame.grid_rowconfigure(0, weight=1)
        self.general_frame.grid_rowconfigure(1, weight=1)
        self.general_frame.grid_columnconfigure(0, weight=1)
        self.general_frame.grid_columnconfigure(1, weight=1)

        # Top left: Robot with difficulty levels
        self.top_left_frame = tk.Frame(self.general_frame, bg="black", highlightthickness=0)
        self.top_left_frame.grid(row=0, column=0, sticky="nsew")

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
        self.top_right_frame.grid(row=0, column=1, sticky="nsew")

        self.friend_button = tk.Button(self.top_right_frame, text="👥", font=("Arial", 200), bg="black", fg="white", command=self.start_friend_game, relief=tk.FLAT)
        self.friend_button.pack(anchor="center")

        # Bottom left: Quit button
        self.bottom_left_frame = tk.Frame(self.general_frame, bg="black", highlightthickness=0)
        self.bottom_left_frame.grid(row=1, column=0, sticky="nsew")

        self.quit_button = tk.Button(self.bottom_left_frame, text="Quit ❌", font=("Arial", 80), bg="black", fg="red", command=self.on_closing, relief=tk.FLAT)
        self.quit_button.pack(anchor="center")

        # Bottom right: BMA button leading to rules and documentation
        self.bottom_right_frame = tk.Frame(self.general_frame, bg="black", highlightthickness=0)
        self.bottom_right_frame.grid(row=1, column=1, sticky="nsew")

        self.bma_button = tk.Button(self.bottom_right_frame, text="BMA", font=("Arial", 80), bg="gray", fg="white", command=self.show_bma_options, relief=tk.FLAT)
        self.bma_button.pack(anchor="center")

    def start_game(self, difficulty):
        # Start the game with the selected difficulty
        messagebox.showinfo("Start Game", f"Starting game with {difficulty} difficulty.")
        # Here you could initialize the chessboard and other game components

    def start_friend_game(self):
        # Start a game against a friend
        messagebox.showinfo("Play Against Friend", "Starting game against a friend.")
        # Here you could initialize the chessboard and other game components

    def show_bma_options(self):
        # Show options for rules and documentation
        messagebox.showinfo("BMA", "BMA Options: Spieleregeln and Dokumentation.")
        # You could also create a new window to display the rules and documentation

    def clear_screen(self):
        # Clear the current screen
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_closing(self):
        # Handle the closing event
        self.root.destroy()
        messagebox.showinfo("Auf Wiedersehen", "Das Programm wird jetzt beendet.")

if __name__ == "__main__":
    # Main program: Initialize and start the GUI
    root = tk.Tk()
    app = ChessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
