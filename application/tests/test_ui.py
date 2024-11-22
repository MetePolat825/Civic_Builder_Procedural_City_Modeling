import pytest
import tkinter as tk
from user_interface import App

def test_ui():
    root = tk.Tk()  # Create a new Tkinter root window
    app = App(root)  # Initialize the app
    assert root.winfo_exists()  # Ensure the root window exists
    assert isinstance(app, App)  # Ensure the App is initialized properly
