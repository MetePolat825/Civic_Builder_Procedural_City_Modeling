# detect_builds.py

import os
import cv2
import time
import numpy as np
import warnings
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def extract_features(model_selection, extract_feature, input_folder):
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

    # Create output folders
    output_folder = "./input_output_files/annotated_output_images"
    obj_folder = "./input_output_files/output_obj_files"
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(obj_folder, exist_ok=True)

    # Check for input images
    if len(os.listdir(input_folder)) == 0:
        raise ValueError("No input images found in the specified folder.")

    # Start time for prediction
    start_time = time.time()

    # Iterate over each image file in the folder
    for image_file in os.listdir(input_folder):
        image_path = os.path.join(input_folder, image_file)
        img = cv2.imread(image_path)

        # Perform inference
        outputs = predictor(img)

        # Visualize and save predictions
        visualizer = Visualizer(img[:, :, ::-1], metadata=None, scale=0.8, instance_mode=ColorMode.IMAGE_BW)
        out = visualizer.draw_instance_predictions(outputs["instances"].to("cpu"))

        # Save annotated image
        output_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_annotated.jpg")
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
                contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    # Simplify the contour to reduce points and create sharper edges
                    epsilon = 0.01 * cv2.arcLength(contour, True)  # Adjust epsilon for more or less simplification
                    simplified_contour = cv2.approxPolyDP(contour, epsilon, True)

                    # Create vertices in the OBJ format (x, y, z)
                    for pt in simplified_contour:
                        vertices.append(f"v {pt[0][0]} {pt[0][1]} 0")  # Assuming z=0 for 2D representation

                    # Create faces based on the vertices added
                    for j in range(1, len(simplified_contour) - 1):
                        obj_faces.append(f"f {vertex_index} {vertex_index + j} {vertex_index + j + 1}")

                    # Update vertex index for the next contour
                    vertex_index += len(simplified_contour)

        # Write to a single .obj file for this image
        obj_filename = f"{os.path.splitext(image_file)[0]}.obj"
        obj_file_path = os.path.join(obj_folder, obj_filename)

        with open(obj_file_path, 'w') as obj_file:
            obj_file.write("\n".join(vertices) + "\n")
            obj_file.write("\n".join(obj_faces) + "\n")

    print(f"Extracted features of type {extract_feature} from {len(os.listdir(input_folder))} images in {time.time()-start_time:.2f} seconds.")
