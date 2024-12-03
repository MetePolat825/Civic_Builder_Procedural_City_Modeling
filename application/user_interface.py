from os import path, listdir,startfile
import webbrowser
from threading import Thread  # For running the UI in a separate thread to avoid freezing
import sys
import subprocess
import json
import os

import tkinter as tk
import customtkinter as ctk

from cv2 import imread, cvtColor, COLOR_BGR2RGB

from PIL import Image as PILImage, ImageTk

from detect_buildings import extract_features


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Civic Builder")

        # Load and set the icon
        self.set_icon()

        # Set default customtkinter appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Set the default window size and position
        root.geometry("1250x750")  # Width x Height    
        
        # Create all frames for the application
        self.sidebar_frame = ctk.CTkFrame(root, width=150, fg_color=None, corner_radius=0, border_color="black", border_width=2)
        self.detection_frame = ctk.CTkFrame(root)
        self.paths_frame = ctk.CTkFrame(root)
        self.post_processing_frame = ctk.CTkFrame(root)
        self.run_frame = ctk.CTkFrame(root)
        self.all_frames = [self.detection_frame,self.paths_frame,self.post_processing_frame,self.run_frame]
        
        # Load logo
        logo_path = path.join(path.dirname(__file__), 'media', 'civic_builder.png')
        pil_image = PILImage.open(logo_path)
        new_width = int(pil_image.width * 0.4)
        new_height = int(pil_image.height * 0.4)
        resized_image = pil_image.resize((new_width, new_height))
        self.logo_image = ImageTk.PhotoImage(resized_image)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
        self.logo_label.pack(pady=10, padx=10)
        
        self.user_preferences = self.get_user_preferences()
        
        # Initialize attributes
        self.input_folder_path = self.user_preferences.get("input_folder_path", "")
        self.output_2d_folder_path = self.user_preferences.get("output_2d_folder_path", "")
        self.output_3d_folder_path = self.user_preferences.get("output_3d_folder_path", "")
        self.blender_path = self.user_preferences.get("blender_path", "")
        
        # test run all frames, generate variables. Better implementation needed but will work for now!
        self.show_paths_frame()
        self.show_detection_frame()
        self.show_post_processing_frame()
        self.show_run_frame()

        self.current_frame = None  
        
        # Sidebar Buttons
        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="Civic Builder\n 3D feature extraction solutions.", anchor="w", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10, padx=10, fill="x")
        
        self.paths_button = ctk.CTkButton(self.sidebar_frame, text="📂 Input/Output Paths", command=self.show_paths_frame)
        self.paths_button.pack(pady=10, padx=10, fill="x")

        self.run_button = ctk.CTkButton(self.sidebar_frame, text="⏯️ Run Extraction", command=self.show_run_frame)
        self.run_button.pack(pady=10, padx=10, fill="x")

        self.basics_label = ctk.CTkLabel(self.sidebar_frame, text=" ")
        self.basics_label.pack(padx=10, fill="x")
        
        self.detection_button = ctk.CTkButton(self.sidebar_frame, text="🔍 Detection Configuration", command=self.show_detection_frame)
        self.detection_button.pack(pady=10, padx=10, fill="x")
        
        self.post_processing_button = ctk.CTkButton(self.sidebar_frame, text="🔧 Post Processing", command=self.show_post_processing_frame)
        self.post_processing_button.pack(pady=10, padx=10, fill="x")
        
        self.basics_label = ctk.CTkLabel(self.sidebar_frame, text=" ")
        self.basics_label.pack(padx=10, fill="x")
        
        self.help_button = ctk.CTkButton(self.sidebar_frame, text="📚 Documentation", command=self.open_help)
        self.help_button.pack(pady=10, padx=10, fill="x")

        self.about_button = ctk.CTkButton(self.sidebar_frame, text="ℹ️ About", command=self.show_about)
        self.about_button.pack(pady=10, padx=10, fill="x")

        self.exit_button = ctk.CTkButton(self.sidebar_frame, text="Quit to Desktop", command=self.exit_app, fg_color="red")
        self.exit_button.pack(pady=10, padx=10, fill="x")

        self.info_label = ctk.CTkLabel(self.sidebar_frame, text="Civic Builder v. 1.0", anchor="w")
        self.info_label.pack(pady=10, padx=10)  

        # Sidebar toggle for light/dark mode
        self.dark_mode_switch = ctk.CTkSwitch(self.sidebar_frame, text="Light Mode", command=self.toggle_mode)
        self.dark_mode_switch.pack(pady=10, padx=60, fill="x",anchor="center")
        
        # Pack the sidebar
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        
        # default frame redraw
        self.show_paths_frame()
    
    def get_user_preferences(self):
        """Get user preferences from a configuration file."""
        user_preferences = {
            "input_folder_path": "",
            "output_2d_folder_path": "",
            "output_3d_folder_path": "",
            "blender_path": ""
        }
        try:
            with open("user_preferences.json", "r") as file:
                user_preferences = json.load(file)
        except FileNotFoundError:
            print("User preferences file not found. Using default settings.")
            self.save_user_preferences(user_preferences)
        except Exception as e:
            print(f"Error loading user preferences: {e}")
            raise
        return user_preferences

    def save_user_preferences(self, user_preferences):
        """Save user preferences to a configuration file."""
        try:
            with open("user_preferences.json", "w") as file:
                json.dump(user_preferences, file, indent=4)
        except Exception as e:
            print(f"Error saving user preferences: {e}")
            raise

        self.user_preferences = self.get_user_preferences()
        self.input_folder_path = self.user_preferences.get("input_folder_path", "")
        self.output_2d_folder_path = self.user_preferences.get("output_2d_folder_path", "")
        self.output_3d_folder_path = self.user_preferences.get("output_3d_folder_path", "")
        self.blender_path = self.user_preferences.get("blender_path", "")

    def save_preferences_after_run(self):
        """Save user preferences after a successful run."""
        user_preferences = {
            "input_folder_path": self.input_folder_path,
            "output_2d_folder_path": self.output_2d_folder_path,
            "output_3d_folder_path": self.output_3d_folder_path,
            "blender_path": self.blender_path
        }
        self.save_user_preferences(user_preferences)

    def toggle_mode(self):
        """Toggle between dark and light modes."""
        current_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")
        
    def depopulate_frame(self, frame: ctk.CTkFrame):
        """Destroy all widgets in a given ctk.CTkFrame (frame) parameter. Best used before redrawing a frame."""
        if frame:
            for widget in frame.winfo_children():
                widget.destroy()  # Completely removes the widget from the frame

    def show_frame(self, frame):
        """Hide all opened frames and display the specified frame."""
        # Hide all frames currently opened
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

        # Add instructions textbox in the left frame
        instructions_frame = ctk.CTkFrame(left_frame)
        instructions_frame.pack(anchor="w", padx=5, pady=5, fill="both", expand=True)

        self.instructions_textbox = ctk.CTkTextbox(
            instructions_frame,
            font=("Arial", 12),
            width=300, 
            height=100, 
            wrap="word"
        )

        self.instructions_textbox.insert(
            "0.0",
            text="Select below a detection model to use for feature extraction from imagery.\n\nFor further details on each model, access documentation by clicking the help buttons."
        )

        self.instructions_textbox.grid(row=0, column=1, padx=10, pady=10)

        # Load help image and resize it
        help_image = tk.PhotoImage(file="media/help.png").subsample(6, 6)  # Adjust subsample to resize

        # Help button for documentation
        help_button = ctk.CTkButton(instructions_frame, image=help_image, text="", 
                                    command=lambda: self.open_help("model_selection.html"))
        help_button.image = help_image  # Keep a reference to avoid garbage collection
        help_button.grid(row=0, column=0, padx=10, pady=10)
        

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
        self.feature_label = ctk.CTkLabel(left_frame, text="Select 3D Feature to Extract:",font=("Arial", 14))
        self.feature_label.pack(pady=5)

        # Feature options
        self.feature_options = [
            "Building Footprints",
            "(Not implemented) Trees/Vegetation",
            "(Not implemented) Roads using GIS",
            "(Not implemented) Water Bodies"
        ]
        
        # Add instructions textbox for feature options
        feature_instructions_frame = ctk.CTkFrame(left_frame)
        feature_instructions_frame.pack(anchor="w", padx=5, pady=5, fill="both", expand=True)

        self.feature_instructions_textbox = ctk.CTkTextbox(
            feature_instructions_frame,
            font=("Arial", 12),
            width=450,  # Set appropriate width
            height=20,  # Optionally set height
            wrap="word"
        )

        self.feature_instructions_textbox.insert(
            "0.0",
            text="Select below the features you wish to extract from input imagery."
        )

        self.feature_instructions_textbox.grid(row=0, column=1, padx=5, pady=10)

        # Dropdown variable for feature selection
        if not hasattr(self, 'feature_var'):
            self.feature_var = tk.StringVar(value=self.feature_options[0])  # Set default value if not already set

        # Dropdown menu for feature selection
        self.feature_dropdown = ctk.CTkOptionMenu(
            left_frame,
            variable=self.feature_var,  # This holds the currently selected feature
            values=self.feature_options   # Pass the list of feature options directly
        )
        self.feature_dropdown.pack(padx=10, pady=10)

        # Create the canvas or image to display on the left (visualization or example image)
        self.canvas_label = ctk.CTkLabel(right_frame, text="Example of Extracted Features in Blender", font=("Arial", 16,"bold"))
        self.canvas_label.pack(pady=10)
        self.canvas_desc_box = ctk.CTkTextbox(
            right_frame,
            font=("Arial", 12),
            width=375,  # Set appropriate width
            height=20,  # Optionally set height
            wrap="word"
        )

        self.canvas_desc_box.insert(
            "0.0",
            text="Civic Builder extracts 3D feature fooprints from imagery."
        )

        self.canvas_desc_box.pack(pady=10)

        # Create the canvas to show the visualization (if relevant) on the left side
        self.canvas = ctk.CTkCanvas(right_frame, width=500, height=500, bg="white")
        self.canvas.pack(pady=10)

        # Load the image using PIL to avoid zooming issues
        img_path = "media/detection_example.png"
        pil_img = PILImage.open(img_path)
        tk_img = ImageTk.PhotoImage(pil_img)

        # Calculate the center coordinates for placing the image
        canvas_width = 500  # Adjust this based on your canvas width
        canvas_height = 500  # Adjust this based on your canvas height
        img_width, img_height = pil_img.size
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2

        # Create the image on the canvas
        self.canvas.create_image(x, y, anchor="nw", image=tk_img)  # anchor="nw" aligns the image to the northwest corner

        # Keep a reference to the image to prevent garbage collection
        self.canvas.image = tk_img

        # Display the detection frame
        self.show_frame(self.detection_frame)
        
    def select_input_folder(self):
        """Select input folder."""
        folder = tk.filedialog.askdirectory()
        if folder:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, folder)

    def select_output_folder(self):
        """Select output folder."""
        folder = tk.filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            
    def show_paths_frame(self):
        """Show Input/Output Paths section."""
        
        # Depopulate the frame to clear old content
        self.depopulate_frame(self.paths_frame)

        # Create a frame for the left column (image)
        left_frame = ctk.CTkFrame(self.paths_frame)
        left_frame.pack(side="left", padx=20, pady=10)

        # Create a frame for the right column (input/output options)
        right_frame = ctk.CTkFrame(self.paths_frame)
        right_frame.pack(side="left", padx=20, pady=10)

        # Add label for title in the right frame
        self.paths_label = ctk.CTkLabel(right_frame, text="Select Input/Output Paths", font=("Arial", 16))
        self.paths_label.pack(pady=10)
        
        # Create a frame for the description box and help button
        desc_frame = ctk.CTkFrame(right_frame)
        desc_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.canvas_desc_box = ctk.CTkTextbox(
            desc_frame,
            font=("Arial", 12),
            width=300,  # Set appropriate width
            height=100,  # Optionally set height
            wrap="word"
        )

        self.canvas_desc_box.insert(
            "0.0",
            text="Welcome to Civic Builder! In order to extract features, please select your imagery and  output paths. "
                "\n"
                "\n"
                "For further details on valid imagery, access documentation by clicking the help buttons."
        )

        self.canvas_desc_box.grid(row=0, column=1, padx=10, pady=10)
        
        # Load help image and resize it
        help_image = tk.PhotoImage(file="media/help.png").subsample(6, 6)  # Adjust subsample to resize

        # Help button for documentation
        help_button = ctk.CTkButton(desc_frame, image=help_image, text="", 
                                    command=lambda: self.open_help("import_imagery.html"))
        help_button.image = help_image  # Keep a reference to avoid garbage collection
        help_button.grid(row=0, column=0, padx=10, pady=10)

        # Input folder selection
        self.input_label = ctk.CTkLabel(right_frame, text="Select Input Images Folder:")
        self.input_label.pack(pady=5)

        self.input_entry = ctk.CTkEntry(right_frame, placeholder_text="Input Folder", width=300)
        self.input_entry.insert(0, self.input_folder_path)
        self.input_entry.pack(pady=5)

        self.input_folder_button = ctk.CTkButton(right_frame, text="Browse for input folder...", 
                                                command=lambda: self.update_path("input"), width=300)
        self.input_folder_button.pack(pady=5)

        # Output folder for Annotated 2D Images
        self.output_2d_label = ctk.CTkLabel(right_frame, text="Select Output Folder for Annotated 2D Imagery:")
        self.output_2d_label.pack(pady=5)

        self.output_2d_entry = ctk.CTkEntry(right_frame, placeholder_text="Output 2D Folder", width=300)
        self.output_2d_entry.insert(0, self.output_2d_folder_path)
        self.output_2d_entry.pack(pady=5)

        self.output_2d_folder_button = ctk.CTkButton(right_frame, text="Browse for 2D output folder...", 
                                                    command=lambda: self.update_path("output_2d"), width=300)
        self.output_2d_folder_button.pack(pady=5)

        # Output folder for 3D Footprint OBJ Files
        self.output_3d_label = ctk.CTkLabel(right_frame, text="Select Output Folder for Extracted 3D .OBJ Files:")
        self.output_3d_label.pack(pady=5)

        self.output_3d_entry = ctk.CTkEntry(right_frame, placeholder_text="Output 3D Folder", width=300)
        self.output_3d_entry.insert(0, self.output_3d_folder_path)
        self.output_3d_entry.pack(pady=5)

        self.output_3d_folder_button = ctk.CTkButton(right_frame, text="Browse for 3D output folder...", 
                                                    command=lambda: self.update_path("output_3d"), width=300)
        self.output_3d_folder_button.pack(pady=10)
        
        self.next_steps_box = ctk.CTkTextbox(
            right_frame,
            font=("Arial", 12),
            width=400,  # Set appropriate width
            height=20,  # Optionally set height
            wrap="word"
        )

        self.next_steps_box.insert(
            "0.0",
            text="Proceed to the \"Run Extraction\" screen to extract features from imagery."
        )

        self.next_steps_box.pack(padx=10, pady=10)

        # Left side image (Input example)
        self.canvas_desc_label_left = ctk.CTkLabel(left_frame, text="Examples of Valid Input Images:\nSatellite Imagery", font=("Arial", 14))
        self.canvas_desc_label_left.pack(pady=10)

        self.canvas_left = ctk.CTkCanvas(left_frame, width=300, height=300, bg="white")
        self.canvas_left.pack(pady=10,padx=10)

        img_left = tk.PhotoImage(file="media/inputoutput_example_1.png")
        self.canvas_left.create_image(150, 150, image=img_left)
        self.canvas_left.image = img_left

        # Right side image (Output example)
        self.canvas_desc_label_right = ctk.CTkLabel(left_frame, text="Examples of Valid Input Images:\nGoogle Maps Screenshots", font=("Arial", 14))
        self.canvas_desc_label_right.pack(pady=10,padx=10)

        self.canvas_right = ctk.CTkCanvas(left_frame, width=300, height=300, bg="white")
        self.canvas_right.pack(pady=10,padx=10)

        img_right = tk.PhotoImage(file="media/inputoutput_example_2.png")
        self.canvas_right.create_image(150, 150, image=img_right)
        self.canvas_right.image = img_right
        
        self.next_steps_box.pack(padx=10, pady=10)

        # Button to go to the Run Extraction frame
        self.run_extraction_button = ctk.CTkButton(right_frame, text="⏯️ Proceed to Run Extraction ⏯️", 
                                                   command=self.show_run_frame, width=300,fg_color="green")
        self.run_extraction_button.pack(pady=10)

        # Show the updated paths frame
        self.show_frame(self.paths_frame)

    def update_path(self, path_type):
        """Update the path for input or output folders."""
        folder = tk.filedialog.askdirectory()
        if folder:  # Only update if a folder is selected
            if path_type == "input":
                self.input_folder_path = folder
                self.input_entry.delete(0, "end")
                self.input_entry.insert(0, self.input_folder_path)
            elif path_type == "output_2d":
                self.output_2d_folder_path = folder
                self.output_2d_entry.delete(0, "end")
                self.output_2d_entry.insert(0, self.output_2d_folder_path)
            elif path_type == "output_3d":
                self.output_3d_folder_path = folder
                self.output_3d_entry.delete(0, "end")
                self.output_3d_entry.insert(0, self.output_3d_folder_path)

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
        self.post_processing_label = ctk.CTkLabel(right_frame, text="Post Processing of Contours", font=("Arial", 14,"bold"))
        self.post_processing_label.pack(pady=10)

        # Add instructions textbox in the right frame
        instructions_frame = ctk.CTkFrame(right_frame)
        instructions_frame.pack(anchor="w", padx=5, pady=5, fill="both", expand=True)

        self.instructions_textbox = ctk.CTkTextbox(
            instructions_frame,
            font=("Arial", 12),
            width=300,  # Set appropriate width
            height=100,  # Optionally set height
            wrap="word"
        )

        self.instructions_textbox.insert(
            "0.0",
            text="Select a post-processing algorithm to refine building contours.\n"
                 "You can re-run the tool to generate new footprints and fine tune.\n"
                 "Algorithms are suited to different goals, with varying levels of detail."
        )

        self.instructions_textbox.grid(row=0, column=1, padx=10, pady=10)

        # Load help image and resize it
        help_image = tk.PhotoImage(file="media/help.png").subsample(6, 6)  # Adjust subsample to resize

        # Help button for documentation
        help_button = ctk.CTkButton(instructions_frame, image=help_image, text="", 
                                    command=lambda: self.open_help("post_processing.html"))
        help_button.image = help_image  # Keep a reference to avoid garbage collection
        help_button.grid(row=0, column=0, padx=10, pady=10)

        # Dropdown for contour post-processing algorithms in the right frame
        self.post_process_options = [
            "Simplify Contours",
            "Smooth Contours",
            "Fill Holes",
            "Bounding Boxes",
            "Convex Hulls"  # New option added
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
            ("Simplify Contours", 
            "Default. Use when contours are too detailed."),
            
            ("Smooth Contours", 
            "Use this when countours are too jagged."),
            
            ("Fill Holes", 
            "Use when contours have many gaps."),
            
            ("Bounding Boxes", 
            "Use when simple bounding boxes are needed with low detail."),
            
            ("Convex Hulls", 
            "Use when simple convex hulls are needed with low detail.")
        ]
        
        self.canvas_desc_label = ctk.CTkLabel(right_frame, text="Available Algorithms:", font=("Arial", 14,"bold"))
        self.canvas_desc_label.pack(pady=10)
        
        # Display descriptions of algorithms in the right frame
        for title, description in algorithm_descriptions:
            title_label = ctk.CTkLabel(right_frame, text=title + ": " + description, font=("Arial", 12))
            title_label.pack(anchor="w", padx=5)


        self.canvas_label = ctk.CTkLabel(left_frame, text="Latest 2D Output:", font=("Arial", 14,"bold"))
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

        # Configure grid layout for the run_frame
        self.run_frame.grid_rowconfigure(0, weight=1)  # Top rows for main content
        self.run_frame.grid_columnconfigure(0, weight=1)  # Left frame
        self.run_frame.grid_columnconfigure(1, weight=1)  # Log frame
        self.run_frame.grid_rowconfigure(1, weight=0)  # Bottom row for progress bar

        # Create a frame for the left column (controls)
        left_frame = ctk.CTkFrame(self.run_frame)
        left_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        # Run title label
        self.run_title_label = ctk.CTkLabel(left_frame, text="Feature Extraction", font=("Arial", 16))
        self.run_title_label.pack(pady=10)
        
        # Create a frame for the description box and help button
        desc_frame = ctk.CTkFrame(left_frame)
        desc_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Description box using CTkTextbox
        self.canvas_desc_box = ctk.CTkTextbox(
            desc_frame,
            font=("Arial", 12),
            width=200,  # Set appropriate width
            height=160,  # Optionally set height
            wrap="word"
        )

        self.canvas_desc_box.insert(
            "0.0",
            text=(
                "After setting options, run the extraction from this window.\n\n"
                "Data to be extracted will include:\n"
                "1. Annotated Images with Detection Confidence Metrics.\n"
                "2. Generated .OBJ footprint files.\n\n"
                "Data will be saved to the output folders specified."
                
            )
        )
        self.canvas_desc_box.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Load help image and resize it
        help_image = tk.PhotoImage(file="media/help.png").subsample(6, 6)  # Adjust subsample to resize

        # Help button for documentation
        help_button = ctk.CTkButton(desc_frame, image=help_image, text="", 
                                    command=lambda: self.open_help("detection_process.html"))
        help_button.image = help_image  # Keep a reference to avoid garbage collection
        help_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.run_button = ctk.CTkButton(left_frame, text="⏯️ Run Feature Extraction ⏯️", command=self.run_feature_extraction, fg_color="green", font=("Arial", 16))
        self.run_button.pack(pady=10)

        # Create a frame for the log in the second column (log_frame)
        log_frame = ctk.CTkFrame(self.run_frame)
        log_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        # Log window label
        self.log_label = ctk.CTkLabel(log_frame, text="Extraction Log:", font=("Arial", 14))
        self.log_label.pack(pady=10)

        # Create a Text widget for the log window (for real-time print output)
        self.log_text = tk.Text(log_frame, height=15, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#333333", fg="white", font=("Arial", 12))
        self.log_text.pack(padx=20, pady=10, fill="both", expand=True)  # Make it expand to fill space

        # Redirect print statements to the log window
        self.redirect_output_to_log()

        # Create a frame for progress bar and feedback at the bottom
        progress_frame = ctk.CTkFrame(self.run_frame)
        progress_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")  # Span both columns

        self.progressbar_label = ctk.CTkLabel(progress_frame, text="Progress of Extraction Process:", wraplength=550, pady=10)
        self.progressbar_label.pack(pady=10)

        self.progressbar = ctk.CTkProgressBar(master=progress_frame)
        self.progressbar.pack(padx=20, pady=10, fill="x")  # Stretch to fill the frame
        self.progressbar.set(0)  # Initialize progress bar

        self.feedback_label = ctk.CTkLabel(progress_frame, text="", font=("Arial", 14), text_color="green")
        self.feedback_label.pack(pady=10)

        self.bar_progress = 0

        # Show the updated frame
        self.show_frame(self.run_frame)
            
        # Create a frame for action buttons under the progress bar
        actions_frame = ctk.CTkFrame(progress_frame)
        actions_frame.pack(padx=20, pady=10, fill="x", expand=True)
        
        self.next_steps_label = ctk.CTkLabel(actions_frame, text="Next Steps Shortcuts:", wraplength=550, pady=10)
        self.next_steps_label.grid(row=0, column=1, padx=20, pady=10, sticky="n")

        # Button to open the export directory for 3D OBJ files
        open_export_button = ctk.CTkButton(
            actions_frame, 
            text="📂 Open 3D Export Directory", 
            command=self.open_export_directory, 
        )
        open_export_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Button to open Blender application
        open_blender_button = ctk.CTkButton(
            actions_frame, 
            text="🖌️ Open Blender and Visualize Output", 
            command=self.open_blender, 
        )
        open_blender_button.grid(row=1, column=1, padx=20, pady=10, sticky="n")

        # Button to go to the detection configuration frame
        open_config_button = ctk.CTkButton(
            actions_frame, 
            text="⚙️ Configure Civic Builder Further", 
            command=self.show_config_frame, 
        )
        open_config_button.grid(row=1, column=2, padx=20, pady=10, sticky="e")
        
        # Configure columns to evenly distribute the buttons
        actions_frame.grid_columnconfigure(0, weight=1)  # Left column
        actions_frame.grid_columnconfigure(1, weight=1)  # Center column
        actions_frame.grid_columnconfigure(2, weight=1)  # Right column

    def redirect_output_to_log(self):
        """Redirect the print output to the log window (Text widget)."""

        class LogRedirector:
            def __init__(self, widget):
                self.widget = widget

            def write(self, message):
                """Write the message to the Text widget."""
                # Check if the message is from pytest
                if not message.startswith("INTERNALERROR>") and not message.startswith("ERROR>") and not message.startswith("WARN>") and not message.startswith("AssertionError"):
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
        except Exception as e:
            print(f"Error setting Civic Builder icon: {e}")

    def run_feature_extraction(self):
        """Run the feature extraction."""
        
        #pre_run_test()  # Run the pre-run test
        
        # Clear log before starting
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Clear feedback label at the start
        self.feedback_label.configure(text="", font=("Arial", 14))

        if not self.model_var or not self.feature_var.get():
            # Show a popup message if model or feature have not been selected
            tk.messagebox.showerror("Error", "Detection model and target feature must be selected!")
            return  # Stop further execution of the function
        
        if not self.input_entry.get() or not self.output_2d_entry.get() or not self.output_3d_entry.get():
            # Show a popup message if at least one of the folders is not selected
            tk.messagebox.showerror("Error", "All input and output folders must be selected before run!")
            return  # Stop further execution of the function
        
        model_selection = self.model_var.get()
        extract_feature = self.feature_var.get()
        input_folder = self.input_entry.get()
        output_2d_folder = self.output_2d_entry.get()
        output_3d_folder = self.output_3d_entry.get()

        # set global variable to use in detect_buildings.py
        global export_post_process_algorithm
        export_post_process_algorithm = self.post_process_algorithm.get()
        
        errors = []
        if not input_folder:
            errors.append("Input folder not selected. Please select input folder before running extraction.")
        elif not path.isdir(input_folder):
            errors.append(f"Selected input folder path is invalid: {input_folder}")
            
        if not output_2d_folder:
            errors.append("Output 2D folder not selected. Please select output annotations folder before running extraction.")
        elif not path.isdir(output_2d_folder):
            errors.append(f"Selected output 2D folder path is invalid: {output_2d_folder}")
            
        if not output_3d_folder:
            errors.append("Output 3D folder not selected. Please select output geometry folder before running extraction.")
        elif not path.isdir(output_3d_folder):
            errors.append(f"Selected output 3D folder path is invalid: {output_3d_folder}")
            
        if errors:
            print("======\nWarning! Encountered errors when running:\n======")
            for error in errors:
                print(f"ERROR: {error}")
            return
        
        self.save_preferences_after_run() # Save the preferences after running the extraction
        
        print("======\nSelected Parameters:\n======",
              "\nModel selection --> ",model_selection,
              "\nExtract feature --> ", extract_feature,
              "\nInput folder --> ",input_folder,
              "\nOutput_2d_folder --> ",output_2d_folder,
              "\nOutput_3d_folder --> ",output_3d_folder,
              "\nPost Processing: --> ",export_post_process_algorithm,
              "\n======\nRunning feature extraction...\n======\n")
        
        # Disable the button and reset the progress bar
        self.run_button.configure(state="disabled")
        self.progressbar.set(0)
        
        # Create and start a new thread for the extraction process
        extraction_thread = Thread(
            target=self.extract_features_in_thread,
            args=(model_selection, extract_feature, input_folder, output_2d_folder,output_3d_folder,export_post_process_algorithm,)
        )
        extraction_thread.start()    
        
    def extract_features_in_thread(self, model_selection, extract_feature, input_folder,output_2d_folder,output_3d_folder,export_post_process_algorithm):
        """Perform the feature extraction in a separate thread."""
        try:
            extract_features(model_selection, extract_feature, input_folder, output_2d_folder,output_3d_folder, export_post_process_algorithm,self.progressbar,self.feedback_label)
        except Exception as e:
            # Handle exceptions and inform the user
            tk.messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Re-enable the button once extraction is complete
            self.run_button.configure(state="normal")        
        
    def open_help(self,page_name ="index.html"):
        """Open documentation given a specified page."""
        documentation_path = path.abspath('../documentation/'+ page_name)
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
        version_label = ctk.CTkLabel(self.about_window, text="Version 1.0", font=("Arial", 12))
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
        """Load the latest contour image to display from the previously selected directory."""
        # Fallback, get the path to the first file in the 'output_2d_folder_path' directory
        example_image_path = 'media/detection_annotation_example.jpg'
        image_path = example_image_path
        
        if path.exists(self.output_2d_folder_path):
            files = [f for f in listdir(self.output_2d_folder_path) if path.isfile(path.join(self.output_2d_folder_path, f))]
            if files:
                image_path = path.join(self.output_2d_folder_path, files[0])
            else:
                image_path = example_image_path
        else:
            image_path = example_image_path
            
        img = imread(image_path)

        # Convert to RGB (from BGR used by OpenCV)
        img_rgb = cvtColor(img, COLOR_BGR2RGB)

        # Convert to PIL Image
        img_pil = PILImage.fromarray(img_rgb)

        # Convert to a Tkinter-compatible image
        self.img_tk = ImageTk.PhotoImage(img_pil)

        # Display the image on canvas
        self.canvas.create_image(0, 0, anchor='nw', image=self.img_tk)
        
    def open_export_directory(self):
        """Opens the directory where the 3D OBJ files are exported."""
        export_dir = self.output_3d_entry.get()  # Ensure this is defined elsewhere
        if export_dir and path.isdir(export_dir):
            startfile(export_dir)  # On Windows; use subprocess for Mac/Linux
        else:
            tk.messagebox.showerror("Error", "Export directory not found or invalid.")

    def open_blender(self):
        """Opens Blender application and runs a script named blender_main."""
        self.blender_path = r"C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe"  # Default path
        if not path.exists(self.blender_path):
            blender_path = tk.filedialog.askopenfilename(
                title="Locate Blender Executable", 
                filetypes=[("Executable Files", "*.exe")]
            )
        if self.blender_path and path.exists(self.blender_path):
            print("Default Blender path found. Starting blender...")
            script_path = path.abspath("blender/blender_main.py")  # path to civic builder addon script to use in blender
            if path.exists(script_path):
                try:
                    subprocess.Popen([self.blender_path, "--python", script_path])  # Open Blender and run the script
                    print("Civic Builder configuration script found. Setting up the Blender environment...")
                except Exception as e:
                    tk.messagebox.showerror("Error", f"An error occurred while opening Blender: {e}")
            else:
                tk.messagebox.showerror("Error", f"Blender script not found: {script_path}")
        else:
            tk.messagebox.showerror("Error", "Blender executable not found.")

    def show_config_frame(self):
        """Navigates to the detection configuration frame."""
        self.show_frame(self.detection_frame)