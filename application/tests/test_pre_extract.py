import os
import pytest

def test_input_images_exist():
    input_folder = "path_to_input_images"
    assert len(os.listdir(input_folder)) > 0, "Input folder is empty."
    
    valid_formats = ['.jpg', '.png']
    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)
        if not any(file.endswith(ext) for ext in valid_formats):
            pytest.fail(f"Invalid image format for file {file}. Expected .jpg or .png.")
