import os
import cv2
import time
import numpy as np
import warnings
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from customtkinter import CTkProgressBar

from post_processing import simplify_contours, smooth_contours, fill_holes, bounding_boxes, convex_hulls # use for user selection of post processing algorithm

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Mapping of imported post processing algorithms for user selections in the GUI
POST_PROCESSING_ALGORITHMS = {
    "Simplify Contours": simplify_contours,
    "Smooth Contours": smooth_contours,
    "Fill Holes": fill_holes,
    "Bounding Boxes": bounding_boxes,
    "Convex Hulls": convex_hulls
}

def process_contours(mask, selected_algorithm):
    # Get contours from the mask
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Apply the selected post-processing algorithm
    if selected_algorithm in POST_PROCESSING_ALGORITHMS:
        contours = POST_PROCESSING_ALGORITHMS[selected_algorithm](contours)
    else:
        raise ValueError(f"Unknown algorithm: {selected_algorithm}")

    return contours

def flatten_contours(contours):
    """
    Ensure that contours are laid flat on the XY plane
    (by ensuring all Z values are zero, without additional rotations).
    """
    flattened_contours = []
    for contour in contours:
        # Ensure that all Z values are 0, leaving the contour in its original orientation
        flattened_contour = []
        for pt in contour:
            # Simply set the Z coordinate to 0 to lay it flat on the XY plane
            flattened_contour.append([pt[0][0], pt[0][1], 0])

        flattened_contours.append(np.array(flattened_contour))
    
    return flattened_contours

def extract_features(model_selection, extract_feature, input_folder, output_2d_folder, output_3d_folder, export_post_process_algorithm, progressbar):
    """
    Perform feature extraction from satellite images based on the selected model and feature type.
    
    Parameters:
        model_selection (int): Selected model index.
        extract_feature (str): The feature to extract.
        input_folder (str): Path to the input folder containing images.
    """
    # Configure model weights based on selection
    if model_selection == 1:
        MODEL_WEIGHTS_PATH = "./prebuilt_detect_models/model_roboflow_default_2k_iter/model_trained_default_set.pth"
    elif model_selection == 2:
        MODEL_WEIGHTS_PATH = "./prebuilt_detect_models/model_roboflow_optimized_5k_iter/model_optimized_5k_iter.pth"
    else:
        MODEL_WEIGHTS_PATH = "./prebuilt_detect_models/model_roboflow_default_2k_iter/model_trained_default_set.pth"
    
    # Configuration file path and number of classes config
    CONFIG_FILE_PATH = "COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"
    NUM_CLASSES = 3  # Adjust based on your model's training

    print(f"Extracting features for: {extract_feature}")

    # Set up configuration for inference
    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cuda"  # or "cpu" if GPU is unavailable
    cfg.merge_from_file(model_zoo.get_config_file(CONFIG_FILE_PATH))

    # Specify the path to the saved trained weights
    cfg.MODEL.WEIGHTS = MODEL_WEIGHTS_PATH
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = NUM_CLASSES
    cfg.INPUT.MASK_FORMAT = 'bitmask'

    # Initialize the predictor
    predictor = DefaultPredictor(cfg)

    # Create output folders. Replace with custom paths later.
    output_folder = output_2d_folder
    obj_folder = output_3d_folder
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(obj_folder, exist_ok=True)

    # Check for input images
    if len(os.listdir(input_folder)) == 0:
        raise ValueError("No input images found in the specified folder.")

    # Start time for prediction
    start_time = time.time()

    count_of_images = len(os.listdir(input_folder))
    weight_per_image = 1 / count_of_images
    progress_value = 0  # start progress from 0
    
    # Iterate over each image file in the folder
    for image_file in os.listdir(input_folder):
        print("Processing image...")
        image_path = os.path.join(input_folder, image_file)
        img = cv2.imread(image_path)

        # Perform inference
        outputs = predictor(img)

        # Visualize and save predictions
        visualizer = Visualizer(img[:, :, ::-1], metadata=None, scale=0.8, instance_mode=ColorMode.IMAGE_BW)
        out = visualizer.draw_instance_predictions(outputs["instances"].to("cpu"))

        # Save annotated image
        output_path = os.path.join(output_2d_folder, f"{os.path.splitext(image_file)[0]}_annotated.jpg")
        cv2.imwrite(output_path, out.get_image()[:, :, ::-1])  # Convert RGB to BGR for OpenCV and save

        # Create .obj file for all detected buildings in this image
        instances = outputs["instances"].to("cpu")
        masks = instances.pred_masks.numpy()

        vertices = []  # To hold all vertices for this image
        obj_faces = []  # To hold all face definitions for this image
        vertex_index = 1  # Start vertex indexing at 1 for OBJ format

        for i in range(len(instances)):
            if instances.scores[i] >= 0.5:  # Filter out low-confidence detections
                mask = masks[i]
                # Fetch the selected algorithm from the user interface 
                selected_algorithm = export_post_process_algorithm
                
                # Process contours with the selected algorithm
                processed_contours = process_contours(mask, selected_algorithm)

                # Step 2: Flatten the contours to ensure they lie flat on the XY plane (Z = 0)
                flattened_contours = flatten_contours(processed_contours)

                for contour in flattened_contours:
                    # For each contour, create a single ngon
                    face = "f " + " ".join(str(vertex_index + idx) for idx in range(len(contour)))
                    obj_faces.append(face)

                    # Add vertices for the current contour
                    for pt in contour:
                        vertices.append(f"v {pt[0]} {pt[1]} 0")  # Set Z to 0

                    vertex_index += len(contour)

        # Write to a single .obj file for this image
        obj_filename = f"{os.path.splitext(image_file)[0]}.obj"
        obj_file_path = os.path.join(obj_folder, obj_filename)

        with open(obj_file_path, 'w') as obj_file:
            obj_file.write("\n".join(vertices) + "\n")
            obj_file.write("\n".join(obj_faces) + "\n")
        
        progress_value += weight_per_image
        progressbar.set(progress_value)
        
        print("Finished processing image...")

    print(f"Extracted features of type {extract_feature} from {len(os.listdir(input_folder))} images in {time.time()-start_time:.2f} seconds.")
