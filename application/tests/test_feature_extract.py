import pytest

from detect_buildings import extract_features

def test_feature_extraction():
    try:
        extract_features(
            model_selection=1,  # example model selection
            extract_feature="building",  # example feature type
            input_folder="path_to_input_images", 
            output_2d_folder="path_to_output_2d", 
            output_3d_folder="path_to_output_3d", 
            export_post_process_algorithm="Simplify Contours", 
            progressbar=None
        )
    except Exception as e:
        pytest.fail(f"Feature extraction failed: {e}")
