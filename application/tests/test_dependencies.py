import importlib
import pytest

# List of dependencies to test
required_modules = [
    'cv2', 'numpy', 'customtkinter', 'detectron2', 'PIL', 'os', 'sys', 'warnings'
]

def test_dependencies():
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            pytest.fail(f"Required module {module} is not installed or cannot be imported.")
