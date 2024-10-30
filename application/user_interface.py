import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser  # For opening the local HTML documentation
import time  # To handle splash screen timing
import threading  # For running the splash screen in a separate thread

class SplashScreen:
    """Class to create a splash screen."""
    def __init__(self, root):
        self.splash = tk.Toplevel(root)
        self.splash.title("Loading...")
        self.splash.geometry("400x200")  # Set the size of the splash screen
        self.splash.overrideredirect(True)  # Remove the title bar
        self.center_window()

        # Placeholder for splash screen content
        self.label = tk.Label(self.splash, text="Loading Civic Builder...\nPlease wait.", font=("Arial", 16))
        self.label.pack(expand=True)

        # Show the splash screen
        self.splash.after(3000, self.close)  # Close after 3 seconds

    def center_window(self):
        """Centers the splash screen on the screen."""
        self.splash.update_idletasks()  # Update "requested size" from geometry manager
        width = self.splash.winfo_width()
        height = self.splash.winfo_height()
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f'{width}x{height}+{x}+{y}')

    def close(self):
        """Close the splash screen."""
        self.splash.destroy()

class App:
    def __init__(self, master, run_extraction_callback):
        self.master = master
        self.master.title("Civic Builder")

        # Load and set the icon
        self.set_icon()

        # Set the default window size and position
        self.master.geometry("600x400")  # Width x Height
        self.center_window()

        # Load and display the placeholder image
        self.placeholder_image = tk.PhotoImage(file="civic_builder.png")  # Ensure this image is in the correct format
        self.image_label = tk.Label(master, image=self.placeholder_image)
        self.image_label.pack(side=tk.RIGHT, padx=10, pady=10)

        # Description label
        self.description_label = tk.Label(
            master, 
            text="Civic Builder: Automate extraction of features from satellite imagery.", 
            wraplength=550, 
            justify="center"
        )
        self.description_label.pack(pady=10)

        # Model selection
        self.model_label = tk.Label(master, text="Select a Model:")
        self.model_label.pack()

        self.model_var = tk.IntVar()
        self.model_options = [
            "Roboflow default 2k iteration detection model.",
            "Roboflow optimized 5k iteration detection model. (India, Rural)",
            "Paris SpaceNet dataset model. (Europe, Urban)",
            "Shanghai SpaceNet dataset model. (Asia, Urban)",
            "Las Vegas SpaceNet dataset model. (U.S.)",
            "Khartoum SpaceNet dataset model. (Middle East, Urban)",
        ]
        
        self.model_dropdown = tk.OptionMenu(master, self.model_var, *self.model_options)
        self.model_dropdown.pack(pady=5)

        # Feature selection
        self.feature_label = tk.Label(master, text="Select Feature to Extract:")
        self.feature_label.pack()

        self.feature_var = tk.IntVar()
        self.feature_options = [
            "Building footprints",
            "Trees (Not implemented)",
            "Roads (Not implemented)",
            "Water (Not implemented)",
        ]
        
        self.feature_dropdown = tk.OptionMenu(master, self.feature_var, *self.feature_options)
        self.feature_dropdown.pack(pady=5)

        # Input folder selection
        self.input_label = tk.Label(master, text="Select Input Image Folder:")
        self.input_label.pack(pady=5)

        self.input_folder_button = tk.Button(master, text="Browse", command=self.select_input_folder)
        self.input_folder_button.pack(pady=5)

        # Run button
        self.run_button = tk.Button(master, text="Run Feature Extraction", command=self.run_feature_extraction)
        self.run_button.pack(pady=10)

        # Exit button
        self.exit_button = tk.Button(master, text="Exit", command=self.exit_app)
        self.exit_button.pack(pady=5)

        # Help button
        self.help_button = tk.Button(master, text="Help", command=self.open_help)
        self.help_button.pack(pady=5)

        # About button
        self.about_button = tk.Button(master, text="About", command=self.show_about)
        self.about_button.pack(pady=5)

        # Status label
        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

        # Initialize variables
        self.input_folder = ""

    def set_icon(self):
        """Set the window icon."""
        try:
            self.master.iconbitmap("civic_builder.ico")  # Use .ico format for Windows
            print("Icon set using .ico format")
        except Exception as e:
            print(f"Error setting icon: {e}")

    def center_window(self):
        """Centers the Tkinter window on the screen."""
        self.master.update_idletasks()  # Update "requested size" from geometry manager
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def select_input_folder(self):
        """Open a dialog to select the input folder."""
        self.input_folder = filedialog.askdirectory()
        self.status_label.config(text=f"Selected folder: {self.input_folder}")

    def run_feature_extraction(self):
        """Run the feature extraction process based on user inputs."""
        model_selection = self.model_var.get() + 1  # Convert to index
        extract_feature_int = self.feature_var.get()  # Already an index
        
        if model_selection not in range(1, 7):
            messagebox.showerror("Error", "Invalid model selection.")
            return
        
        extract_feature = self.feature_options[extract_feature_int]
        if extract_feature == "Trees (Not implemented)":
            messagebox.showerror("Error", "Feature extraction for trees is not implemented.")
            return

        # Call the extraction function passed from main.py
        self.run_extraction_callback(model_selection, extract_feature, self.input_folder)

    def open_help(self):
        """Open the local HTML documentation."""
        # Construct the path to the documentation folder, assuming it's one level up
        documentation_path = os.path.abspath('../documentation/index.html')  # Adjust the path to point one directory up
        url = 'file:///' + documentation_path.replace('\\', '/')  # Ensure using forward slashes
        print(f"Opening documentation at: {url}")  # Debugging line
        webbrowser.open(url)

    def show_about(self):
        """Show an about message."""
        messagebox.showinfo("About", "Civic Builder: Automated feature extraction from satellite imagery.\nVersion: 0.1")

    def exit_app(self):
        """Exit the application."""
        self.master.quit()

def run_app():
    """Run the Tkinter app."""
    root = tk.Tk()

    # Load the main app after a delay
    def load_main_app():

        # Create and show the main application window
        app = App(root, run_extraction_callback=lambda model, feature, folder: print(f"Running extraction with {model}, {feature}, {folder}"))
        root.mainloop()

    # Start loading the main app in a separate thread to keep the splash screen responsive
    threading.Thread(target=load_main_app).start()

if __name__ == "__main__":
    run_app()
