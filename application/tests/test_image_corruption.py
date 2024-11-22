import os
import cv2
import pytest

def test_image_integrity():
    input_folder = "path_to_input_images"
    for image_file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, image_file)
        img = cv2.imread(file_path)
        assert img is not None, f"Image {image_file} is corrupted and cannot be read."
