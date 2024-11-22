import pytest
import sys

def pre_run_test():
    print("Running pre-run tests...")
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        sys.exit("Tests failed.")
    else:
        print("All tests passed successfully.")
