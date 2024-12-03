from sys import exit

from customtkinter import CTk

from user_interface import App  # App contains the main user interface.

def main():
    """
    Main entry point for the Civic Builder: Procedural City Modeling project.
    Handles project initialization and starts the user interface.
    """
    try:
        print("Starting Civic Builder: Procedural City Modeling...")

        # Set up the Tkinter root window and initialize App.
        root = CTk()
        app = App(root)
        root.mainloop() 

    except KeyboardInterrupt:
        print("\Keyboard interrupted initiatilization. Exiting...")
        exit(0)
    except Exception as e:
        print(f"Terminated, error occurred when initializing Civic Builder: {e}")
        exit(1)

if __name__ == "__main__":
    main()