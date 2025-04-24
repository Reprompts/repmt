import os
import subprocess
import sys
from pathlib import Path

def main():
    """Entry point for the repmt command"""
    try:
        # Get the path to frontend.py in the installed package
        package_dir = Path(__file__).parent
        frontend_path = str(package_dir / 'frontend.py')
        
        if not os.path.exists(frontend_path):
            raise FileNotFoundError(f"Could not find frontend.py at {frontend_path}")
        
        print(f"Launching repmt from: {frontend_path}")  # Debug info
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', frontend_path])
    except Exception as e:
        print(f"Error launching repmt: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()