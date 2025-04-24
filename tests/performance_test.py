# Copyright (c) 2025 RePromptsQuest
# Licensed under the MIT License

import timeit
import reprompt

def test_analysis_speed():
    test_code = """
import reprompt
repo_path = "."
reprompt.backend.scan_repo(repo_path)
    """
    time = timeit.timeit(test_code, number=10)/10
    assert time < 2.0  # Adjust threshold as needed

if __name__ == "__main__":
    test_analysis_speed()
    print("Performance test passed!")