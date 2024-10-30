import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser  # For opening the local HTML documentation
import time  # To handle splash screen timing
import threading  # For running the splash screen in a separate thread

class App:
    def __init__(self, master, run_extraction_callback=None):
        self.master = master
        self.master.title("Civic Builder")

        # Load and set the icon
        self.set_icon()

        # Set the default window size and position
        self.master.geometry("600x400")  # Width x Height
        self.center_window()

        # Placeholder for extraction callback; provide a default if none is passed
        if run_extraction_callback:
            self.run_extraction_callback = run_extraction_callback
        else:
            self.run_extraction_callback = self.default_extraction_callback

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

        self.model_options = [
            "Roboflow default 2k iteration detection model.",
            "Roboflow optimized 5k iteration detection model. (India, Rural)",
            "Paris SpaceNet dataset model. (Europe, Urban)",
            "Shanghai SpaceNet dataset model. (Asia, Urban)",
            "Las Vegas SpaceNet dataset model. (U.S.)",
            "Khartoum SpaceNet dataset model. (Middle East, Urban)",
        ]
        
        self.model_var = tk.StringVar()
        self.model_var.set(self.model_options[0])
        
        self.model_dropdown = tk.OptionMenu(master, self.model_var, self.model_options)
        self.model_dropdown.pack(pady=5)

        # Feature selection
        self.feature_label = tk.Label(master, text="Select Feature to Extract:")
        self.feature_label.pack()

        self.feature_options = [
            "Building footprints",
            "Trees (Not implemented)",
            "Roads (Not implemented)",
            "Water (Not implemented)",
        ]
        
        self.feature_var = tk.StringVar()
        self.feature_var.set(self.feature_options[0])  # Set the default value
        
        self.feature_dropdown = tk.OptionMenu(master, self.feature_var, self.feature_options)
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
        # Retrieve selected model and feature by their names
        selected_model_text = self.model_var.get()
        selected_feature_text = self.feature_var.get()
        
        # Get the index of the selected model from the model options list
        try:
            model_selection = self.model_options.index(selected_model_text) + 1  # Convert to 1-based index
        except ValueError:
            messagebox.showerror("Error", "Invalid model selection.")
            return
        
        # Verify feature selection
        if selected_feature_text not in self.feature_options:
            messagebox.showerror("Error", "Invalid feature selection.")
            return
        
        # Check if feature extraction is implemented for the selected feature
        if selected_feature_text == "Trees (Not implemented)":
            messagebox.showerror("Error", "Feature extraction for trees is not implemented.")
            return
        
        # Run the extraction callback with selected model, feature, and folder
        self.run_extraction_callback(model_selection, selected_feature_text, self.input_folder)


    def open_help(self):
        """Open the local HTML documentation."""
        documentation_path = os.path.abspath('../documentation/index.html')
        url = 'file:///' + documentation_path.replace('\\', '/')
        webbrowser.open(url)

    def show_about(self):
        """Show an about message."""
        messagebox.showinfo("About", "Civic Builder: Automated feature extraction from satellite imagery.\nVersion: 0.1")

    def exit_app(self):
        """Exit the application."""
        self.master.quit()

    def default_extraction_callback(self, model_selection, extract_feature, input_folder):
        """Default callback function if no extraction callback is provided."""
        print(f"Running extraction with model: {model_selection}, feature: {extract_feature}, folder: {input_folder}")


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
