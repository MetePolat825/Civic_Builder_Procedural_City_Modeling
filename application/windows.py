# windows.py
import tkinter as tk
from tkinter import ttk

class BaseWindow:
    def __init__(self, master, title="Window", size="400x300"):
        self.window = tk.Toplevel(master)
        self.window.title(title)
        self.window.geometry(size)

        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError("You must override create_widgets() in the subclass")

class FeatureExtractionWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master, title="Feature Extraction", size="500x400")

    def create_widgets(self):
        label = ttk.Label(self.window, text="Feature Extraction Module", font=("Helvetica", 14))
        label.pack(pady=20)

        # Placeholder for future feature extraction options
        extract_button = ttk.Button(self.window, text="Start Feature Extraction")
        extract_button.pack(pady=10)

class CityGenerationWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master, title="City Generation", size="500x400")

    def create_widgets(self):
        label = ttk.Label(self.window, text="City Generation Module", font=("Helvetica", 14))
        label.pack(pady=20)

        # Placeholder for future city generation options
        generate_button = ttk.Button(self.window, text="Generate 3D City")
        generate_button.pack(pady=10)