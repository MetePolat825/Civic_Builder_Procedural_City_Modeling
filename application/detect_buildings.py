from os import path, listdir, makedirs
from time import time
from warnings import filterwarnings

from cv2 import findContours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, imwrite, imread
from numpy import uint8, array

from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

# Post-processing algorithm imports
from post_processing import simplify_contours, smooth_contours, fill_holes, bounding_boxes, convex_hulls

# Suppress specific warnings
filterwarnings("ignore", category=FutureWarning)
filterwarnings("ignore", category=UserWarning)

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
    contours, _ = findContours(mask.astype(uint8), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)

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

        flattened_contours.append(array(flattened_contour))
    
    return flattened_contours

def extract_features(model_selection, extract_feature, input_folder, output_2d_folder, output_3d_folder, export_post_process_algorithm, progressbar):
    """
    Perform feature extraction from satellite images based on the selected model and feature type.
    
    Parameters:
        model_selection (int): Selected model index.
        extract_feature (str): The feature to extract.
        input_folder (str): Path to the input folder containing images.
        output_2d_folder (str): Path to the output folder for 2D annotated images.
        output_3d_folder (str): Path to the output folder for 3D OBJ files.
        export_post_process_algorithm (str): Selected post-processing algorithm.
        progressbar (CTkProgressBar): Progress bar to update during processing.
    """
    
    # Configure model weights based on selection
    if model_selection == 1:
        MODEL_WEIGHTS_PATH = "./prebuilt_detect_models/model_roboflow_default_2k_iter/model_trained_default_set.pth"
        CONFIG_FILE_PATH = "./config/mask_rcnn_R_101_FPN_3x_2k_iter.yaml"  # Local path to the config file
    elif model_selection == 2:
        MODEL_WEIGHTS_PATH = "./prebuilt_detect_models/model_roboflow_optimized_5k_iter/model_optimized_5k_iter.pth"
        CONFIG_FILE_PATH = "./config/mask_rcnn_R_101_FPN_3x_5k_iter.yaml"  # Local path to the config file
    else:
        MODEL_WEIGHTS_PATH = "./prebuilt_detect_models/model_roboflow_default_2k_iter/model_trained_default_set.pth"
        CONFIG_FILE_PATH = "./config/mask_rcnn_R_101_FPN_3x_5k_iter.yaml"  # Local path to the config file

    NUM_CLASSES = 3  # Adjust based on your model's training
    print(f"Extracting features for: {extract_feature}")

    # Set up configuration for inference
    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cuda"  # or "cpu" if GPU is unavailable
    cfg.merge_from_file(CONFIG_FILE_PATH)
    cfg.MODEL.WEIGHTS = MODEL_WEIGHTS_PATH  # Set the model weights path
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = NUM_CLASSES  # Set the number of classes

    # Initialize the predictor
    predictor = DefaultPredictor(cfg)

    # Create output folders. Replace with custom paths later.
    output_folder = output_2d_folder
    obj_folder = output_3d_folder
    makedirs(output_folder, exist_ok=True)
    makedirs(obj_folder, exist_ok=True)

    # Check for input images
    if len(listdir(input_folder)) == 0:
        raise ValueError("No input images found in the specified folder.")

    # Start time for prediction
    start_time = time()

    count_of_images = len(listdir(input_folder))
    weight_per_image = 1 / count_of_images
    progress_value = 0  # start progress from 0
    
    # Iterate over each image file in the folder
    for image_file in listdir(input_folder):
        print(f"Processing image: {image_file}")
        image_path = path.join(input_folder, image_file)
        img = imread(image_path)

        # Perform inference
        outputs = predictor(img)

        # Visualize and save predictions
        visualizer = Visualizer(img[:, :, ::-1], metadata=None, scale=0.8, instance_mode=ColorMode.IMAGE_BW)
        out = visualizer.draw_instance_predictions(outputs["instances"].to("cpu"))

        # Save annotated image
        output_path = path.join(output_2d_folder, f"{path.splitext(image_file)[0]}_annotated.jpg")
        imwrite(output_path, out.get_image()[:, :, ::-1])  # Convert RGB to BGR for OpenCV and save

        # Create .obj file for all detected buildings in this image
        instances = outputs["instances"].to("cpu")
        masks = instances.pred_masks.numpy()

        vertices = []  # To hold all vertices for this image
        obj_faces = []  # To hold all face definitions for this image
        vertex_index = 1  # Start vertex indexing at 1 for OBJ format

        # Add the big polygon that spans the entire image
        height, width, _ = img.shape
        big_polygon = [
            [0, 0, 0],
            [width, 0, 0],
            [width, height, 0],
            [0, height, 0]
        ]
        big_polygon_vertices = [f"v {pt[0]} {pt[1]} {pt[2]}" for pt in big_polygon]
        big_polygon_faces = [f"f {vertex_index} {vertex_index+1} {vertex_index+2} {vertex_index+3}"]

        # Write the big polygon to a separate .obj file
        big_polygon_filename = f"{path.splitext(image_file)[0]}_imagery.obj"
        big_polygon_file_path = path.join(obj_folder, big_polygon_filename)

        with open(big_polygon_file_path, 'w') as big_polygon_file:
            big_polygon_file.write("\n".join(big_polygon_vertices) + "\n")
            big_polygon_file.write("\n".join(big_polygon_faces) + "\n")

        # Process building footprints
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

        # Write to a single .obj file for building footprints
        footprints_filename = f"{path.splitext(image_file)[0]}_footprints.obj"
        footprints_file_path = path.join(obj_folder, footprints_filename)

        with open(footprints_file_path, 'w') as footprints_file:
            footprints_file.write("\n".join(vertices) + "\n")
            footprints_file.write("\n".join(obj_faces) + "\n")
        
        print(f"Succesfully extracted features: {image_file}\n")
        
        progress_value += weight_per_image
        progressbar.set(progress_value)

    print(f"=====\nSUCCESS:Extracted features of type {extract_feature} from {len(listdir(input_folder))} images in {time()-start_time:.2f} seconds.\n=====")
