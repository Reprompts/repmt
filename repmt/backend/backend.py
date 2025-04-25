# Copyright (c) 2025 RePromptsQuest
# Licensed under the MIT License

import os
import ast
import fnmatch  # To support wildcard matching

# ----------------------------
# Configuration for Ignored Items and File Limits
# ----------------------------
IGNORE_FOLDERS = {
    'node_modules', '.git', '.venv', 'venv', 'env',
    '__pycache__', '.mypy_cache', 'dist', 'build',
    '.next', 'Pods', 'Carthage', 'DerivedData', 'target',
    'repmt.egg-info'   # <-- Now ignored.
}

def is_virtual_env(directory):
    return os.path.exists(os.path.join(directory, "pyvenv.cfg"))

IGNORE_EXTENSIONS = {
    '.pyc', '.class', '.jar', '.so', '.dll', '.exe', '.o',
    '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.zip', '.tar.gz', '.db',
    '.sqlite', '.ico', '.ttf', '.woff', '.pdf', '.min.js', '.map'
}

MAX_FILE_SIZE = 100_000  # 100 KB maximum file size
DEFAULT_MAX_PROMPT_LENGTH = 10000  # Maximum characters allowed in prompt parts

def trim_text(text, max_chars=10000):
    """Trims the text if it exceeds max_chars."""
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... (truncated)"
    return text

# ----------------------------
# File Summarization Functions
# ----------------------------
def summarize_file(filepath, max_lines=20):
    """
    Reads the first `max_lines` of a text file and returns a summary.
    If the file cannot be decoded as text, returns a note that it is binary.
    """
    summary_lines = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for i in range(max_lines):
                line = f.readline()
                if not line:
                    break
                summary_lines.append(line.rstrip())
    except Exception as e:
        return f"Error reading file: {e}"
    summary = "\n".join(summary_lines)
    return trim_text(summary, max_chars=10000)

# ----------------------------
# Language-Specific Analysis
# ----------------------------
def analyze_python_file(filepath):
    """
    Uses AST to extract defined functions, classes, and imported libraries from a Python file.
    Returns a dictionary with keys: 'functions', 'classes', 'imports'.
    """
    analysis = {"functions": [], "classes": [], "imports": []}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            file_content = file.read()
            tree = ast.parse(file_content, filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)
    except Exception as e:
        analysis["error"] = f"Error analyzing file: {e}"
    return analysis

# ----------------------------
# Repository Scanning
# ----------------------------
def get_directory_structure(root_dir):
    """
    Recursively builds a string representation of the directory structure,
    ignoring dependency folders and virtual environments.
    """
    structure_lines = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out ignored folders and virtual environments.
        dirnames[:] = [
            d for d in dirnames 
            if d not in IGNORE_FOLDERS and not is_virtual_env(os.path.join(dirpath, d))
        ]
        level = dirpath.replace(root_dir, "").count(os.sep)
        indent = " " * 4 * level
        structure_lines.append(f"{indent}{os.path.basename(dirpath)}/")
        subindent = " " * 4 * (level + 1)
        for f in filenames:
            structure_lines.append(f"{subindent}{f}")
    full_structure = "\n".join(structure_lines)
    return trim_text(full_structure, max_chars=DEFAULT_MAX_PROMPT_LENGTH)

def scan_repo(repo_path):
    """
    Scans the repository for code files and extracts analysis or summary info.
    Skips files with ignored extensions, files that are too large, and those in virtual environments.
    For Python files, uses AST analysis; for others, uses a first-N-lines summary.
    Returns a dictionary mapping relative file paths to analysis/summary.
    """
    repo_analysis = {}
    for dirpath, dirnames, filenames in os.walk(repo_path):
        # Exclude ignored directories and virtual environments.
        dirnames[:] = [
            d for d in dirnames 
            if d not in IGNORE_FOLDERS and not is_virtual_env(os.path.join(dirpath, d))
        ]
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            if ext in IGNORE_EXTENSIONS:
                continue
            full_path = os.path.join(dirpath, file)
            rel_path = os.path.relpath(full_path, repo_path)
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    summary = "File too large to process."
                else:
                    if ext == ".py":
                        summary = analyze_python_file(full_path)
                    else:
                        summary = summarize_file(full_path)
                repo_analysis[rel_path] = summary
            except Exception as e:
                repo_analysis[rel_path] = f"Error processing file: {e}"
    return repo_analysis

def aggregate_imports(repo_analysis):
    """
    Aggregates a unique list of libraries imported in Python files within the repository.
    """
    imports = set()
    for analysis in repo_analysis.values():
        if isinstance(analysis, dict) and "imports" in analysis:
            for imp in analysis.get("imports", []):
                imports.add(imp)
    return list(imports)

# ----------------------------
# Filtering with Include/Exclude (Wildcard Support)
# ----------------------------
def filter_repo_analysis(repo_analysis, include_list=None, exclude_list=None):
    """
    Filters repo_analysis:
      - If include_list is provided, only files whose path matches one of the glob patterns are kept.
      - Files matching any pattern in exclude_list are removed.
    """
    filtered = {}
    for path, data in repo_analysis.items():
        if exclude_list and any(fnmatch.fnmatch(path.lower(), ex.lower()) for ex in exclude_list):
            continue
        if include_list and not any(fnmatch.fnmatch(path.lower(), inc.lower()) for inc in include_list):
            continue
        filtered[path] = data
    return filtered

def build_directory_structure_from_analysis(repo_analysis):
    """
    Builds a directory tree (as a string) from the keys of repo_analysis.
    """
    tree = {}
    for path in repo_analysis.keys():
        parts = path.split(os.sep)
        node = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                node.setdefault("_files", []).append(part)
            else:
                node = node.setdefault(part, {})
    lines = []
    def build_lines(node, indent=0):
        for key in sorted(node.keys()):
            if key == "_files":
                for f in sorted(node[key]):
                    lines.append(" " * 4 * indent + f)
            else:
                lines.append(" " * 4 * indent + key + "/")
                build_lines(node[key], indent+1)
    build_lines(tree)
    return "\n".join(lines)
