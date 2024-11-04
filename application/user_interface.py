import os
import webbrowser
import webbrowser  # For opening the local HTML documentation
import time  # To handle splash screen timing
import threading  # For running the splash screen in a separate thread

import tkinter as tk
from tkinter import filedialog, messagebox, StringVar
import customtkinter as ctk

from detect_buildings import extract_features

class App:
    def __init__(self, root, run_extraction_callback=None):
        self.root = root
        self.root.title("Civic Builder")

        # Load and set the icon
        #self.set_icon()

        # Set default appearance mode
        ctk.set_appearance_mode("dark")  # Let system control the theme by default
        ctk.set_default_color_theme("dark-blue")  # Custom color theme for styling
        
        # pre set darkmode
        #ctk.set_appearance_mode("dark")
        #ctk.set_default_color_theme("dark-blue")

        # Set the default window size and position
        root.geometry("575x700")  # Width x Height
        #self.center_window()
        
        # Sidebar Frame with brighter gray color
        sidebar_frame = ctk.CTkFrame(root, width=150, fg_color=None, corner_radius=0, border_color="black",border_width=2)
        sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")

        # Sidebar toggle for light/dark mode
        self.dark_mode_switch = ctk.CTkSwitch(sidebar_frame, text="Light Mode", command=self.toggle_mode)
        self.dark_mode_switch.pack(pady=10, padx=10)
        
        # Add Help and About buttons in the sidebar
        self.help_button = ctk.CTkButton(sidebar_frame, text="Documentation", command=self.open_help)
        self.help_button.pack(pady=10,padx=10)

        self.about_button = ctk.CTkButton(sidebar_frame, text="About", command=self.show_about)
        self.about_button.pack(pady=10,padx=10)

        # Add additional buttons or information to the sidebar
        self.info_label = ctk.CTkLabel(sidebar_frame, text="Civic Builder v. 0.1", anchor="w")
        self.info_label.pack(pady=10, padx=10)
        
        # define the frames
        user_selections_frame = ctk.CTkFrame(root,border_color="black",border_width=2)        
        run_extraction_frame = ctk.CTkFrame(root,border_color="black",border_width=2)        
        extras_frame = ctk.CTkFrame(root,border_color="black",border_width=2)        
        
        # Pack the frames in the main layout
        user_selections_frame.grid(row=0, column=1, pady=10, padx=10, sticky="ew")  
        run_extraction_frame.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        extras_frame.grid(row=2, column=1, pady=10, padx=10, sticky="ew") 

        # Load and display the placeholder image
        #self.placeholder_image = tk.PhotoImage(file="civic_builder.png")
        #self.image_label = ctk.CTkLabel(master, image=self.placeholder_image)
        #self.image_label.pack(side=ctk.RIGHT, padx=10, pady=10)

        # Description label
        self.description_label = ctk.CTkLabel(
            user_selections_frame, 
            text="Civic Builder: Automate extraction of features from satellite imagery.", 
            wraplength=550, 
            justify="center",
            pady = 10
        )
        self.description_label.pack(padx=5, pady=10)
              
        # Model selection label
        self.model_label = ctk.CTkLabel(user_selections_frame, text="Select a Computer Vision Model:")
        self.model_label.pack(padx=5, pady=5)

        # Model options
        self.model_options = [
            "Roboflow default 2k iteration detection model.",
            "Roboflow optimized 5k iteration detection model.(India, Rural)",
            "Paris SpaceNet dataset model.(Europe, Urban)",
            "Shanghai SpaceNet dataset model.(Asia, Urban)",
            "Las Vegas SpaceNet dataset model.(U.S.)",
            "Khartoum SpaceNet dataset model.(Middle East, Urban)",
        ]

        # Dropdown variable for model selection
        self.model_var = tk.StringVar(value=self.model_options[0])  # Set default value

        # Dropdown menu for model selection
        self.model_dropdown = ctk.CTkOptionMenu(
            user_selections_frame,
            variable=self.model_var,  # This holds the currently selected model
            values=self.model_options   # Pass the list of model options directly
        )
        self.model_dropdown.pack(pady=5)

        # Feature selection label
        self.feature_label = ctk.CTkLabel(user_selections_frame, text="Select Feature to Extract:")
        self.feature_label.pack(pady=5)

        # Feature options
        self.feature_options = [
            "Building footprints",
            "Trees (Not implemented)",
            "Roads (Not implemented)",
            "Water (Not implemented)",
        ]

        # Dropdown variable for feature selection
        self.feature_var = tk.StringVar(value=self.feature_options[0])  # Set default value

        # Dropdown menu for feature selection
        self.feature_dropdown = ctk.CTkOptionMenu(
            user_selections_frame,
            variable=self.feature_var,  # This holds the currently selected feature
            values=self.feature_options   # Pass the list of feature options directly
        )
        self.feature_dropdown.pack(pady=5)
        

        # Input folder selection
        self.input_label = ctk.CTkLabel(user_selections_frame, text="Select Input Images Folder:")
        self.input_label.pack(pady=5)
        
        self.input_entry = ctk.CTkEntry(user_selections_frame, placeholder_text="Input Folder", width=300)
        self.input_entry.pack(pady=5)
        
        self.input_folder_button = ctk.CTkButton(user_selections_frame, text="Browse", command=self.select_input_folder, width=300)
        self.input_folder_button.pack(pady=5)

        # Output folder selection
        self.output_label = ctk.CTkLabel(user_selections_frame, text="Select Output Folder:")
        self.output_label.pack(pady=5)
        
        self.output_entry = ctk.CTkEntry(user_selections_frame, placeholder_text="Output Folder", width=300)
        self.output_entry.pack(pady=5)
        
        self.output_folder_button = ctk.CTkButton(user_selections_frame, text="Browse", command=self.select_output_folder, width=300)
        self.output_folder_button.pack(pady=10)

       # Run and extras
        self.run_label = ctk.CTkLabel(run_extraction_frame, text="After setting options, run the extraction.", wraplength=550, pady=10)
        self.run_label.pack(pady= 10,padx=10)
        
        self.run_button = ctk.CTkButton(run_extraction_frame, text="Run Feature Extraction", command=self.run_feature_extraction, fg_color="green")
        self.run_button.pack(pady=10)
        
        self.progressbar = ctk.CTkProgressBar(master=run_extraction_frame)
        self.progressbar.pack(padx=20, pady=10)
        self.progressbar.set(0)
        self.bar_progress = 0
        
        
        self.exit_button = ctk.CTkButton(extras_frame, text="Exit", command=self.exit_app)
        self.exit_button.pack(pady=10)

    def toggle_mode(self):
        """Toggle between dark and light modes."""
        current_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

    def select_input_folder(self):
        """Select input folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, folder)

    def select_output_folder(self):
        """Select output folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            
    def set_icon(self):
        """Set the window icon."""
        try:
            self.root.iconbitmap("civic_builder.ico")  # Use .ico format for Windows
            print("Icon set using .ico format")
        except Exception as e:
            print(f"Error setting icon: {e}")

    def run_feature_extraction(self):
        """Run the feature extraction."""
        model_selection = self.model_var.get()
        extract_feature = self.feature_var.get()
        input_folder = self.input_entry.get()
        output_folder = self.output_entry.get()
        
        # Disable the button and reset the progress bar
        self.run_button.configure(state="disabled")
        self.progressbar.set(0)
        
        # Create and start a new thread for the extraction process
        extraction_thread = threading.Thread(
            target=self.extract_features_in_thread,
            args=(model_selection, extract_feature, input_folder, output_folder)
        )
        extraction_thread.start()
        
    def extract_features_in_thread(self, model_selection, extract_feature, input_folder, output_folder):
        """Perform the feature extraction in a separate thread."""
        try:
            extract_features(model_selection, extract_feature, input_folder, output_folder, self.progressbar)
        except Exception as e:
            # Handle exceptions and inform the user
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Re-enable the button once extraction is complete
            self.run_button.configure(state="normal")        
        
    def open_help(self):
        """Open documentation."""
        documentation_path = os.path.abspath('../documentation/index.html')
        documentation_path = documentation_path.replace("\\", "/")
        webbrowser.open(f'file:///{documentation_path}')


    def show_about(self):
        """Show about message."""
        messagebox.showinfo("About", "Civic Builder: Version 0.1")

    def exit_app(self):
        """Exit the application."""
        self.root.quit()



def run_app():
    """Run the Tkinter app."""
    root = ctk.CTk()

    # Load the main app after a delay
    def load_main_app():

        # Create and show the main application window
        app = App(root, run_extraction_callback=lambda model, feature, folder: print(f"Running extraction with {model}, {feature}, {folder}"))
        root.mainloop()



