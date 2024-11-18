import cv2
import numpy as np

def simplify_contours(contours):
    """Simplify the contour to reduce the number of points."""
    simplified = []
    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        simplified.append(cv2.approxPolyDP(contour, epsilon, True))
    return simplified

def smooth_contours(contours):
    """Smooth the contour to reduce jagged edges."""
    smoothed = []
    for contour in contours:
        kernel_size = 5
        smoothed_points = cv2.GaussianBlur(contour, (kernel_size, kernel_size), 0)
        smoothed.append(smoothed_points)
    return smoothed

def fill_holes(mask):
    """Fill any holes inside the contours."""
    filled_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(filled_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def bounding_boxes(contours):
    """Create bounding boxes around each contour."""
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        boxes.append(np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]]))
    return boxes

def convex_hulls(contours):
    """Compute the convex hull for each contour."""
    hulls = []
    for contour in contours:
        hulls.append(cv2.convexHull(contour))
    return hulls
