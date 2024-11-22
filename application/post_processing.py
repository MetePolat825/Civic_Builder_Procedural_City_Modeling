from cv2 import arcLength,approxPolyDP,convexHull,findContours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, morphologyEx, MORPH_CLOSE,boundingRect
from numpy import array, uint8, ndarray, logical_or, ones,all

def simplify_contours(contours):
    """Simplify the contour to reduce the number of points."""
    simplified = []
    for contour in contours:
        epsilon = 0.01 * arcLength(contour, True)
        simplified.append(approxPolyDP(contour, epsilon, True))
    return simplified

def smooth_contours(contours, epsilon_factor=0.02):
    """
    Smooth the contours by approximating them with fewer points.
    
    Parameters:
        contours (list): List of contours to smooth.
        epsilon_factor (float): The approximation factor. Smaller values retain more detail.
        
    Returns:
        list: Smoothed contours.
    """
    smoothed = []
    for contour in contours:
        # Epsilon defines the approximation precision as a fraction of the contour perimeter
        epsilon = epsilon_factor *arcLength(contour, closed=True)
        smoothed_contour = approxPolyDP(contour, epsilon, closed=True)
        smoothed.append(smoothed_contour)
    return smoothed

def fill_holes(mask):
    """
    Fill any holes in a binary mask and return the external contours.

    Parameters:
        mask (numpy.ndarray): Binary mask (values 0 or 255).
    
    Returns:
        list: List of filled contours.
    """
    # Ensure the mask is a NumPy array
    if not isinstance(mask, ndarray):
        raise ValueError("Input mask must be a NumPy array.")
    
    # Check mask dimensions
    if len(mask.shape) != 2:
        raise ValueError("Input mask must be a 2D binary image.")

    # Ensure the mask is binary (values 0 and 255)
    if not all(logical_or(mask == 0, mask == 255)):
        raise ValueError("Input mask must be binary with values 0 or 255.")

    # Convert to binary (0 or 255)
    binary_mask = (mask > 0).astype(uint8) * 255

    # Define the kernel for morphological closing
    kernel = ones((5, 5), uint8)

    # Apply morphological closing to fill holes
    filled_mask = morphologyEx(binary_mask, MORPH_CLOSE, kernel)

    # Find external contours from the filled mask
    contours, _ = findContours(filled_mask, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)

    return contours

def bounding_boxes(contours):
    """
    Create bounding boxes around each contour.
    
    Parameters:
        contours (list): List of contours, where each contour is a NumPy array of shape (n, 1, 2).
    
    Returns:
        list: List of bounding box vertices as NumPy arrays.
    """
    boxes = []
    for contour in contours:
        if len(contour) < 1:
            continue  # Skip empty or invalid contours
        
        # Ensure contour is a numpy array of shape (n, 1, 2)
        if not isinstance(contour, ndarray) or contour.shape[1:] != (1, 2):
            raise ValueError("Invalid contour format. Expected numpy array of shape (n, 1, 2).")
        
        x, y, w, h = boundingRect(contour)
        box = array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
        boxes.append(box)
    return boxes

def convex_hulls(contours):
    """Compute the convex hull for each contour."""
    hulls = []
    for contour in contours:
        hulls.append(convexHull(contour))
    return hulls
