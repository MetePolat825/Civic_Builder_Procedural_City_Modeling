# main.py

import sys
import os
import tkinter as tk
import customtkinter as ctk

from user_interface import App  # Import the App class from the user_interface module
from detect_buildings import extract_features  # Import the extract_features function


def initialize_project():
    """
    Initialize the project by loading necessary configurations, data, or assets. 
    Additionally handle automated testing.
    """
    print("Initializing the project...")
    
    # perform pre-start initial tests
    #init_test()
    
    # check external resources all loaded
    
    # check requirements exist with correct versions of over
    
    # check compatible environment


def run_feature_extraction(model_selection, extract_feature, input_folder):
    """
    Wrapper to run the feature extraction process.
    """
    try:
        extract_features(model_selection, extract_feature, input_folder)
        print(f"Features of type {extract_feature} extracted successfully!")
    except Exception as e:
        print(f"Terminated feature extraction due to error: {e}")

def main():
    """
    Main entry point for the Civic Builder: Procedural City Modeling project.
    Handles project initialization and starts the user interface.
    """
    try:
        print("Starting Civic Builder: Procedural City Modeling...")

        # Initialize the project and perform initial tests.
        initialize_project()

        # Set up the Tkinter root window
        root = ctk.CTk()
        app = App(root, run_feature_extraction)  # Pass the extraction function to the UI
        root.mainloop()  # Start the GUI event loop

    except KeyboardInterrupt:
        print("\Keyboard interrupted initiatilization. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Terminated, error occurred when initializing Civic Builder: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
