import os
import webbrowser  # For opening the local HTML documentation
import threading  # For running the UI in a separate thread to avoid freezing
import sys
import time

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

import cv2
import numpy as np

from PIL import Image as PILImage, ImageTk


from detect_buildings import extract_features

class App:
    def __init__(self, root, run_extraction_callback=None):
        self.root = root
        self.root.title("Civic Builder")

        # Load and set the icon
        self.set_icon()

        # Set default appearance mode
        ctk.set_appearance_mode("dark")  # Let system control the theme by default
        ctk.set_default_color_theme("dark-blue")  # Custom color theme for styling

        # Set the default window size and position
        root.geometry("1250x700")  # Width x Height
        #self.center_window()
        
        # Placeholder for selected post-processing algorithm
        self.post_process_algorithm = tk.StringVar()
        
        
        # Define the sidebar frame and other frames for each section
        self.sidebar_frame = ctk.CTkFrame(root, width=150, fg_color=None, corner_radius=0, border_color="black", border_width=2)
        self.detection_frame = ctk.CTkFrame(root)
        self.paths_frame = ctk.CTkFrame(root)
        self.post_processing_frame = ctk.CTkFrame(root)
        self.run_frame = ctk.CTkFrame(root)
        self.all_frames = [self.detection_frame,self.paths_frame,self.post_processing_frame,self.run_frame]
        
        # Load the image using PIL
        logo_path = os.path.join(os.path.dirname(__file__), 'media', 'civic_builder.png')
        pil_image = PILImage.open(logo_path)
        
        # Resize the image to 50% of its original size
        new_width = int(pil_image.width * 0.4)
        new_height = int(pil_image.height * 0.4)
        resized_image = pil_image.resize((new_width, new_height))
        
        # Convert the resized image to a format that Tkinter can use
        self.logo_image = ImageTk.PhotoImage(resized_image)
        
        # Add logo to sidebar using a label
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
        self.logo_label.pack(pady=10, padx=10)  # Add some padding around the logo
        
        # test run all frames, generate variables
        self.show_detection_frame()
        self.show_paths_frame()
        self.show_post_processing_frame()
        self.show_run_frame()
        
        self.current_frame = None  
        # Sidebar Buttons
        
        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="Civic Builder\nIntelligent feature extraction.", anchor="w", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10, padx=10, fill="x")

        # Set uniform width for all buttons by using 'fill="x"'
        self.detection_button = ctk.CTkButton(self.sidebar_frame, text="🔍 Detection Configuration", command=self.show_detection_frame)
        self.detection_button.pack(pady=10, padx=10, fill="x")

        self.paths_button = ctk.CTkButton(self.sidebar_frame, text="📂 Input/Output Paths", command=self.show_paths_frame)
        self.paths_button.pack(pady=10, padx=10, fill="x")

        self.post_processing_button = ctk.CTkButton(self.sidebar_frame, text="🔧 Post Processing", command=self.show_post_processing_frame)
        self.post_processing_button.pack(pady=10, padx=10, fill="x")

        self.run_button = ctk.CTkButton(self.sidebar_frame, text="▶️ Run Extraction", command=self.show_run_frame)
        self.run_button.pack(pady=10, padx=10, fill="x")

        self.linebreak = ctk.CTkLabel(self.sidebar_frame, text=" ")
        self.linebreak.pack(pady=10, padx=10, fill="x")

        # About & Documentation
        self.help_button = ctk.CTkButton(self.sidebar_frame, text="📚 Documentation", command=self.open_help)
        self.help_button.pack(pady=10, padx=10, fill="x")

        self.about_button = ctk.CTkButton(self.sidebar_frame, text="ℹ️ About", command=self.show_about)
        self.about_button.pack(pady=10, padx=10, fill="x")

        # Sidebar toggle for light/dark mode
        self.dark_mode_switch = ctk.CTkSwitch(self.sidebar_frame, text="Light Mode", command=self.toggle_mode)
        self.dark_mode_switch.pack(pady=10, padx=10, fill="x")

        # Exit Button with Red Background
        self.exit_button = ctk.CTkButton(self.sidebar_frame, text="Quit to Desktop", command=self.exit_app, fg_color="red")
        self.exit_button.pack(pady=10, padx=10, fill="x")

        self.info_label = ctk.CTkLabel(self.sidebar_frame, text="Civic Builder v. 0.1", anchor="w")
        self.info_label.pack(pady=10, padx=10)  

        # Pack the sidebar
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        
        # Initial frame
        self.show_detection_frame()
        
        # Load and display the placeholder image
        #self.placeholder_image = tk.PhotoImage(file="civic_builder.png")
        #self.image_label = ctk.CTkLabel(master, image=self.placeholder_image)
        #self.image_label.pack(side=ctk.RIGHT, padx=10, pady=10)

    def toggle_mode(self):
        """Toggle between dark and light modes."""
        current_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")
        
    def depopulate_frame(self, frame):
        """Destroy all widgets in frame for redraw."""
        if frame:
            for widget in frame.winfo_children():
                widget.destroy()  # Completely removes the widget from the frame

    def show_frame(self, frame):
        """Hide all frames and display the specified frame."""
        # Hide all frames
        for f in self.all_frames:
            f.grid_forget()  # Unmap the frame from the grid system each time we redraw

        # Show the specified frame
        frame.grid(row=0, column=1, pady=50, padx=10)
        self.current_frame = frame
        
    def show_detection_frame(self):
        """Show Detection Configuration section."""
        self.depopulate_frame(self.detection_frame)  # depopulate frame before redrawing

        # Create a frame for the left column (image/canvas)
        left_frame = ctk.CTkFrame(self.detection_frame)
        left_frame.pack(side="left", padx=20, pady=10)

        # Create a frame for the right column (text/labels)
        right_frame = ctk.CTkFrame(self.detection_frame)
        right_frame.pack(side="left", padx=20, pady=10)

        # Add label for title in the right frame
        self.detection_label = ctk.CTkLabel(left_frame, text="Detection Configuration", font=("Arial", 16,"bold"))
        self.detection_label.pack(pady=10)
        
        # Model selection label
        self.model_label = ctk.CTkLabel(left_frame, text="Select a Computer Vision Model:",font=("Arial", 14))
        self.model_label.pack(padx=5, pady=5)

        # Add instructions label in the right frame
        self.instructions_label = ctk.CTkLabel(left_frame, text="Select a computer vision model to use for feature extraction from imagery.\nNote that different models have been trained for different regions and purposes.\nDifferent building types and parts of the world require different models.\nCivic Builder allows the selection of the following pre-trained detection models:",
                                               font=("Arial", 12),
                                               anchor="w",
                                               justify ="left")
        
        self.instructions_label.pack(anchor="w", padx=15, pady=5)



        # Model options
        self.model_options = [
            "Fast approximate detection model. (India - Roboflow) ",
            "Optimized 5k iteration detection model. (India - Roboflow)",
            "(Not implemented) Paris specialist model. (Europe - SpaceNet 2)",
            "(Not implemented) Shanghai specialist model. (Asia - SpaceNet 2)",
            "(Not implemented) Las Vegas specialist model. (U.S. - SpaceNet 2)",
            "(Not implemented) Khartoum specialist model. (Middle East - SpaceNet 2)"
        ]

        # Dropdown variable for model selection
        if not hasattr(self, 'model_var'):
            self.model_var = tk.StringVar(value=self.model_options[0])  # Set default value if not already set

        # Dropdown menu for model selection
        self.model_dropdown = ctk.CTkOptionMenu(
            left_frame,
            variable=self.model_var,  # This holds the currently selected model
            values=self.model_options   # Pass the list of model options directly
        )
        self.model_dropdown.pack(pady=5)

        # Feature selection label
        self.feature_label = ctk.CTkLabel(left_frame, text="Select Feature to Extract:",font=("Arial", 14))
        self.feature_label.pack(pady=5)

        # Feature options
        self.feature_options = [
            "Building Footprints",
            "(Not implemented) Trees/Vegetation",
            "(Not implemented) Roads using GIS",
            "(Not implemented) Water Bodies"
        ]
        
        self.instructions_label = ctk.CTkLabel(left_frame, text="Civic builder is able to extract multiple different features from imagery.\nSeparate specially trained models can be used to specifically extract each feature.\nCivic Builder provides multiple of such specifically pre-trained models.\nThe following features are available for extraction:",
                                               font=("Arial", 12),
                                               anchor="w",
                                               justify ="left")
        
        self.instructions_label.pack(anchor="w", padx=15, pady=5)

        # Dropdown variable for feature selection
        if not hasattr(self, 'feature_var'):
            self.feature_var = tk.StringVar(value=self.feature_options[0])  # Set default value if not already set

        # Dropdown menu for feature selection
        self.feature_dropdown = ctk.CTkOptionMenu(
            left_frame,
            variable=self.feature_var,  # This holds the currently selected feature
            values=self.feature_options   # Pass the list of feature options directly
        )
        self.feature_dropdown.pack(pady=5)

        # Help button for documentation in the right frame
        help_button = ctk.CTkButton(left_frame, text="💡 Need Help? Open User Preferences Documentation Here... 💡", command=lambda: self.open_help("model_selection.html"),font=("Arial", 12))
        help_button.pack(pady=20)

        # Create the canvas or image to display on the left (visualization or example image)
        self.canvas_label = ctk.CTkLabel(right_frame, text="Example of Extracted Features in Blender", font=("Arial", 16,"bold"))
        self.canvas_label.pack(pady=10)
        
        self.canvas_desc_label = ctk.CTkLabel(right_frame, text="Civic Builder creates polygonal representations of extracted feature footprints.\nStarting from 2D imagery it uses a computer vision to extract features.\nIt then creates 2D footprint geometry that can be exported into any common 3D program.", font=("Arial", 12))
        self.canvas_desc_label.pack(pady=10)

        # Create the canvas to show the visualization (if relevant) on the left side
        self.canvas = ctk.CTkCanvas(right_frame, width=500, height=500, bg="white")
        self.canvas.pack(pady=10)
        
        img = tk.PhotoImage(file="media/detection_example.png")
        self.canvas.create_image(400, 400, image=img)  # Adjust coordinates as needed
        self.canvas.image = img

        # Display the detection frame
        self.show_frame(self.detection_frame)
        
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
            
    def show_paths_frame(self):
        """Show Input/Output Paths section."""
        
        self.depopulate_frame(self.paths_frame)  # depopulate frame before redrawing

        # Create a frame for the left column (image)
        left_frame = ctk.CTkFrame(self.paths_frame)
        left_frame.pack(side="left", padx=20, pady=10)

        # Create a frame for the right column (input/output options)
        right_frame = ctk.CTkFrame(self.paths_frame)
        right_frame.pack(side="left", padx=20, pady=10)

        # Add label for title in the right frame
        self.paths_label = ctk.CTkLabel(right_frame, text="Input/Output Paths", font=("Arial", 16))
        self.paths_label.pack(pady=10)

        # Description for the canvas in the right frame
        self.canvas_desc_label = ctk.CTkLabel(right_frame, text="While Civic Builder prefers formatted imagery with no annotations\nit is also possible to use images from various sources including Google Earth or GIS.", anchor="w", font=("Arial", 12))
        self.canvas_desc_label.pack(pady=10)

        # Input folder selection
        self.input_label = ctk.CTkLabel(right_frame, text="Select Input Images Folder:")
        self.input_label.pack(pady=5)
        
        # Ensure self.input_folder_path persists
        if not hasattr(self, 'input_folder_path'):
            self.input_folder_path = ""  # Initialize if not already set
        
        # Entry for input folder path
        self.input_entry = ctk.CTkEntry(right_frame, placeholder_text="Input Folder", width=300)
        self.input_entry.insert(0, self.input_folder_path)  # Set previously stored path (if any)
        self.input_entry.pack(pady=5)
        
        self.input_folder_button = ctk.CTkButton(right_frame, text="Browse for input folder...", command=self.select_input_folder, width=300)
        self.input_folder_button.pack(pady=5)

        # Output folder selection
        self.output_label = ctk.CTkLabel(right_frame, text="Select Output Folder:")
        self.output_label.pack(pady=5)
        
        # Ensure self.output_folder_path persists
        if not hasattr(self, 'output_folder_path'):
            self.output_folder_path = ""  # Initialize if not already set
        
        # Entry for output folder path
        self.output_entry = ctk.CTkEntry(right_frame, placeholder_text="Output Folder", width=300)
        self.output_entry.insert(0, self.output_folder_path)  # Set previously stored path (if any)
        self.output_entry.pack(pady=5)
        
        self.output_folder_button = ctk.CTkButton(right_frame, text="Browse for output folder...", command=self.select_output_folder, width=300)
        self.output_folder_button.pack(pady=10)

        # Help button for documentation
        help_button = ctk.CTkButton(right_frame, text="💡 Need Help? Open Imports/Outputs Documentation Here... 💡", command=lambda: self.open_help("import_imagery.html"), font=("Arial", 12))
        help_button.pack(pady=10)
        
        # Left side image (Input example) - Create the canvas to show the visualization (if relevant)
        self.canvas_desc_label_left = ctk.CTkLabel(left_frame, text="Examples of Valid Input Images:\nSatellite Imagery", font=("Arial", 14))
        self.canvas_desc_label_left.pack(pady=10)

        self.canvas_left = ctk.CTkCanvas(left_frame, width=300, height=300, bg="white")
        self.canvas_left.pack(pady=10)

        img_left = tk.PhotoImage(file="media/inputoutput_example_1.png")  # Path to the left image
        self.canvas_left.create_image(150, 150, image=img_left)  # Adjust the coordinates for center positioning
        self.canvas_left.image = img_left  # Keep a reference to the image

        # Right side image (Output example) - Create the canvas to show the output visualization (if relevant)
        self.canvas_desc_label_right = ctk.CTkLabel(left_frame, text="Examples of Valid Input Images:\nGoogle Maps Screenshots", font=("Arial", 14))
        self.canvas_desc_label_right.pack(pady=10)

        self.canvas_right = ctk.CTkCanvas(left_frame, width=300, height=300, bg="white")
        self.canvas_right.pack(pady=10)

        img_right = tk.PhotoImage(file="media/inputoutput_example_2.png")  # Path to the right image
        self.canvas_right.create_image(150, 150, image=img_right)  # Adjust the coordinates for center positioning
        self.canvas_right.image = img_right  # Keep a reference to the image

        # Show the updated paths frame
        self.show_frame(self.paths_frame)

    def show_post_processing_frame(self):
        """Show Post Processing Configuration and Visualization."""
        self.depopulate_frame(self.post_processing_frame)  # depopulate frame before redrawing

        # Create a frame for the left column (image and canvas)
        left_frame = ctk.CTkFrame(self.post_processing_frame)
        left_frame.pack(side="left", padx=20, pady=10)

        # Create a frame for the right column (labels)
        right_frame = ctk.CTkFrame(self.post_processing_frame)
        right_frame.pack(side="left", padx=20, pady=10)

        # Add label for title in the right frame
        self.post_processing_label = ctk.CTkLabel(right_frame, text="Post-Processing of Contours", font=("Arial", 14,"bold"))
        self.post_processing_label.pack(pady=10)

        # Add instructions label in the right frame
        self.instructions_label = ctk.CTkLabel(right_frame, text="Select a post-processing algorithm to refine building contours.", font=("Arial", 12))
        self.instructions_label.pack(anchor="w", padx=5, pady=1)
        self.instructions_label = ctk.CTkLabel(right_frame, text="You can re-run the tool to generate new footprints and fine tune.", font=("Arial", 12))
        self.instructions_label.pack(anchor="w", padx=5, pady=1)
        self.instructions_label = ctk.CTkLabel(right_frame, text="Algorithms are suited to different goals, with varying levels of detail.", font=("Arial", 12))
        self.instructions_label.pack(anchor="w", padx=5, pady=1)
        
        # Dropdown for contour post-processing algorithms in the right frame
        self.post_process_options = [
            "Simplify Contours",
            "Smooth Contours",
            "Fill Holes",
            "Bounding Boxes"
        ]
        
        # Ensure self.post_process_algorithm is initialized once, and retain the last selection
        if not hasattr(self, 'post_process_algorithm'):
            self.post_process_algorithm = tk.StringVar(value=self.post_process_options[0])  # Default value if not already set

        # Dropdown menu for post-processing algorithm selection
        self.post_process_dropdown = ctk.CTkOptionMenu(
            right_frame,
            variable=self.post_process_algorithm,  # This holds the currently selected algorithm
            values=self.post_process_options  # Pass the list of algorithm options directly
        )
        self.post_process_dropdown.pack(pady=10)

            # Add labels for algorithm descriptions in the right frame
        algorithm_descriptions = [
            ("Simplify Contours", "Feature: Reduces the number of points in the contour, making it simpler and more efficient.\nCons: Gets rid of sharp."),
            ("Smooth Contours", "Feature: Smoothens the contour to reduce jagged edges and create a more natural shape.\nCons: High geometry."),
            ("Fill Holes", "Feature: Fills any holes inside the contours to create closed shapes.\nCons: Loses small details."),
            ("Bounding Boxes", "Feature: Creates bounding boxes around each detected contour for easier identification.\nCons: Gets rid of orientation/rotation.")
        ]

        # Display descriptions of algorithms in the right frame
        for title, description in algorithm_descriptions:
            title_label = ctk.CTkLabel(right_frame, text="Algorithm: "+title, font=("Arial", 14, "bold"))
            title_label.pack(anchor="n", padx=30, pady=5)

            description_label = ctk.CTkLabel(right_frame, text=description, font=("Arial", 12))
            description_label.pack(anchor="w", padx=20, pady=5)
            
        help_button = ctk.CTkButton(right_frame, text="💡 Need Help? Open Post Processing Documentation Here... 💡", command=lambda: self.open_help("post_processing.html"),font=("Arial", 12))
        help_button.pack(pady=20)

        self.canvas_label = ctk.CTkLabel(left_frame, text="Example output of latest run:", font=("Arial", 14,"bold"))
        self.canvas_label.pack(pady=10)
        
        self.canvas_desc_label = ctk.CTkLabel(left_frame, text="Post processed representation of the latest run of Civic Builder.", font=("Arial", 12))
        self.canvas_desc_label.pack(pady=10)


        # Create the canvas to show the visualization of contours (in the left frame)
        self.canvas = ctk.CTkCanvas(left_frame, width=500, height=500, bg="white")
        self.canvas.pack(pady=10)

        # Load the default image to visualize
        self.load_image()

        # Display the post-processing frame
        self.show_frame(self.post_processing_frame)
    

    def show_run_frame(self):
        """Show Run Extraction section."""
        
        self.depopulate_frame(self.run_frame)  # depopulate frame before redrawing
        
        # Create a frame for the left column (controls)
        left_frame = ctk.CTkFrame(self.run_frame)
        left_frame.pack(side="left", padx=20, pady=10)

        # Run title label
        self.run_title_label = ctk.CTkLabel(left_frame, text="Run Feature Extraction", font=("Arial", 16))
        self.run_title_label.pack(pady=10)
        
        # Run and extras
        self.run_label = ctk.CTkLabel(left_frame, text="After setting options, run the extraction from this window.\n\nData to be extracted will include:\nAnnotated Images with Detection Confidence Metrics\nGenerated .OBJ footprint files.", wraplength=550, pady=10)
        self.run_label.pack(pady=10, padx=10)
        
        self.run_button = ctk.CTkButton(left_frame, text="Run Feature Extraction", command=self.run_feature_extraction, fg_color="green")
        self.run_button.pack(pady=10)
        
        self.progressbar_label = ctk.CTkLabel(left_frame, text="Progress of Extraction Process:", wraplength=550, pady=10)
        self.progressbar_label.pack(pady=10, padx=10)
        
        self.progressbar = ctk.CTkProgressBar(master=left_frame)
        self.progressbar.pack(padx=20, pady=10)
        self.progressbar.set(0)
        self.bar_progress = 0
        
        help_button = ctk.CTkButton(left_frame, text="💡 Need Help? Open Extraction Documentation Here... 💡", command=lambda: self.open_help("export_output.html"), font=("Arial", 12))
        help_button.pack(pady=10)
        
        # Create a frame for the log in the second column (log_frame)
        log_frame = ctk.CTkFrame(self.run_frame)
        log_frame.pack(side="left", padx=20, pady=10, fill="both", expand=True)  # Fill the available space

        # Log window label
        self.log_label = ctk.CTkLabel(log_frame, text="Extraction Log:", font=("Arial", 14))
        self.log_label.pack(pady=10)

        # Create a Text widget for the log window (for real-time print output)
        self.log_text = tk.Text(log_frame, height=15, width=80, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Arial", 12))
        self.log_text.pack(padx=20, pady=10, fill="both", expand=True)  # Make it expand to fill space

        # Redirect print statements to the log window
        self.redirect_output_to_log()

        # Show the updated frame
        self.show_frame(self.run_frame)

    def redirect_output_to_log(self):
        """Redirect the print output to the log window (Text widget)."""
        
        class LogRedirector:
            def __init__(self, widget):
                self.widget = widget

            def write(self, message):
                """Write the message to the Text widget."""
                self.widget.config(state=tk.NORMAL)  # Enable editing to insert text
                self.widget.insert(tk.END, message)  # Insert the message
                self.widget.yview(tk.END)  # Scroll to the end to show the latest log
                self.widget.config(state=tk.DISABLED)  # Disable editing

            def flush(self):
                pass  # Required for compatibility with the print() function, but we don't need to do anything here

        # Redirect the standard output to the log window
        log_redirector = LogRedirector(self.log_text)
        sys.stdout = log_redirector  # Redirect all print statements to the Text widget
     
    def set_icon(self):
        """Set the window icon."""
        try:
            self.root.iconbitmap("media/civic_builder.ico")  # Use .ico format for Windows
            print("Icon set using .ico format")
        except Exception as e:
            print(f"Error setting icon: {e}")

    def run_feature_extraction(self):
        """Run the feature extraction."""

        if not self.model_var or not self.feature_var:
            # Show a popup message if model or feature have not been selected
            messagebox.showerror("Error", "Detection model and target feature must be selected!")
            return  # Stop further execution of the function
        
        if not self.input_entry or not self.output_entry or self.input_entry == "" or self.output_entry == "":
            # Show a popup message if at least one of the folders is not selected
            messagebox.showerror("Error", "Both input and output folders must be selected!")
            return  # Stop further execution of the function
        
        model_selection = self.model_var.get()
        extract_feature = self.feature_var.get()
        input_folder = self.input_entry.get()
        output_folder = self.output_entry.get()
        
        print("======\nRunning feature extraction with the following:\n======",
              "\nModel selection --> ",model_selection,
              "\nExtract feature -->", extract_feature,
              "\nInput folder -->",input_folder,
              "\nOutput_folder -->",output_folder)
        
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
        
    def open_help(self,page_name ="index.html"):
        """Open documentation given a specified page."""
        documentation_path = os.path.abspath('../documentation/'+ page_name)
        documentation_path = documentation_path.replace("\\", "/")
        webbrowser.open(f'file:///{documentation_path}')


    def show_about(self):
        """Show about message."""
    
        # Close the existing About window if it is already open
        if hasattr(self, 'about_window') and self.about_window.winfo_exists():
            self.about_window.destroy()
        
        # Create a new top-level window
        self.about_window = ctk.CTkToplevel(self.root)  # Assuming self.root is your main CTk window
        self.about_window.title("About Civic Builder")  # Title of the About window
        self.about_window.geometry("400x400")  # Size of the window
        self.about_window.resizable(False, False)  # Disable resizing of the About window

        # Title or Project Name
        title_label = ctk.CTkLabel(self.about_window, text="Civic Builder", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Version
        version_label = ctk.CTkLabel(self.about_window, text="Version 0.1", font=("Arial", 12))
        version_label.pack(pady=5)

        # Description
        description_text = "Civic Builder is an application designed to assist with urban planning and civic engagement.\nIt provides tools to visualize and analyze city data."
        description_label = ctk.CTkLabel(self.about_window, text=description_text, font=("Arial", 10), justify="left")
        description_label.pack(pady=10, padx=20)

        # Links to documentation or website (optional)
        documentation_button = ctk.CTkButton(self.about_window, text="Documentation", command=self.open_help)
        documentation_button.pack(pady=5)

        # Credits Section
        credits_text = "Developed by: Mete Polat at Anglia Ruskin University, 2024\nSpecial thanks: Roboflow, Meta Detectron 2"
        credits_label = ctk.CTkLabel(self.about_window, text=credits_text, font=("Arial", 10), justify="left")
        credits_label.pack(pady=10, padx=20)

        # Close Button
        close_button = ctk.CTkButton(self.about_window, text="Close", command=self.about_window.destroy)
        close_button.pack(pady=10)
        
        # Bring the window to the front and make it focused
        self.about_window.lift()
        self.about_window.focus_force()

    def exit_app(self):
        """Exit the application."""
        self.root.quit()
        
    def load_image(self):
        """Load an example contour image to display."""
        # Get the path to the first file in the 'annotated_output_images' folder in the current directory
        folder_path = os.path.join(os.path.dirname(__file__), 'input_output_files/annotated_output_images')
        example_image_path = os.path.join(folder_path, sorted(os.listdir(folder_path))[0]) if os.listdir(folder_path) else None

        img = cv2.imread(example_image_path)

        # Convert to RGB (from BGR used by OpenCV)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        img_pil = PILImage.fromarray(img_rgb)

        # Convert to a Tkinter-compatible image
        self.img_tk = ImageTk.PhotoImage(img_pil)

        # Display the image on canvas
        self.canvas.create_image(0, 0, anchor='nw', image=self.img_tk)

    def apply_post_processing(self):
        """Apply the selected post-processing algorithm to the contours."""
        selected_algorithm = self.post_process_algorithm.get()

        # Apply selected post-processing algorithm (you need to implement the actual processing logic)
        # For example, if 'Simplify Contours' is selected, apply cv2.approxPolyDP to simplify the contour
        if selected_algorithm == "Simplify Contours":
            self.simplify_contours()
        elif selected_algorithm == "Smooth Contours":
            self.smooth_contours()
        elif selected_algorithm == "Fill Holes":
            self.fill_holes()

    def simplify_contours(self):
        """Simplify the contours using cv2.approxPolyDP."""
        print("Simplifying contours...")
        # Add logic to simplify contours here
        pass

    def smooth_contours(self):
        """Smooth the contours using Gaussian Blur or another method."""
        print("Smoothing contours...")
        # Add logic to smooth contours here
        pass

    def fill_holes(self):
        """Fill holes in the contours (if applicable)."""
        print("Filling holes in contours...")
        # Add logic to fill holes here
        pass

def run_app():
    """Run the Tkinter app."""
    root = ctk.CTk()

    # Load the main app after a delay
    def load_main_app():

        # Create and show the main application window
        app = App(root, run_extraction_callback=lambda model, feature, folder: print(f"Running extraction with {model}, {feature}, {folder}"))
        root.mainloop()



