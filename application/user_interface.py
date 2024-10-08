# user_interface.py
import tkinter as tk
from tkinter import ttk,messagebox  
from windows import FeatureExtractionWindow, CityGenerationWindow

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Civic Builder: Procedural City Modeling")
        self.root.geometry("600x400")
        
        self.create_menu()
    
    def create_menu(self):
        # Creating a menu bar
        menubar = tk.Menu(self.root)

        # Adding 'File' menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Feature Extraction", command=self.open_feature_extraction_window)
        file_menu.add_command(label="City Generation", command=self.open_city_generation_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Adding 'Help' menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_info)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def run(self):
        # Start the main event loop
        self.root.mainloop()

    def open_feature_extraction_window(self):
        # Open a new window for Feature Extraction
        FeatureExtractionWindow(self.root)

    def open_city_generation_window(self):
        # Open a new window for City Generation
        CityGenerationWindow(self.root)

    def show_about_info(self):
        # Simple message box to show 'About' information
        tk.messagebox.showinfo("About", "Civic Builder: Procedural City Modeling\nVersion 1.0")