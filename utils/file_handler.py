import os
import zipfile
from typing import Dict
import tempfile

def process_uploaded_file(file_path: str) -> Dict[str, str]:
    """Process uploaded file and return a dictionary of Python files and their contents."""
    code_files = {}
    
    if file_path.endswith('.zip'):
        # Process zip file
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            temp_dir = tempfile.mkdtemp()
            zip_ref.extractall(temp_dir)
            
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.py'):
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, temp_dir)
                        with open(full_path, 'r', encoding='utf-8') as f:
                            try:
                                code_files[relative_path] = f.read()
                            except UnicodeDecodeError:
                                # Skip files that can't be read as text
                                continue
    else:
        # Process single Python file
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                code_files[os.path.basename(file_path)] = f.read()
            except UnicodeDecodeError:
                raise ValueError("File could not be read as text")
    
    if not code_files:
        raise ValueError("No Python files found in the upload")
    
    return code_files 