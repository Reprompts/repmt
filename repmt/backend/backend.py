# Copyright (c) 2025 RePromptsQuest
# Licensed under the MIT License

import os
import ast
import fnmatch
from typing import List, Dict, Union

# ----------------------------
# Configuration
# ----------------------------

IGNORE_FOLDERS = {
    'node_modules', '.git', '.venv', 'venv', 'env',
    '__pycache__', '.mypy_cache', 'dist', 'build',
    '.next', 'Pods', 'Carthage', 'DerivedData', 'target',
    'repmt.egg-info'
}

IGNORE_EXTENSIONS = {
    '.pyc', '.class', '.jar', '.so', '.dll', '.exe', '.o',
    '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.zip', '.tar.gz', '.db',
    '.sqlite', '.ico', '.ttf', '.woff', '.pdf', '.min.js', '.map'
}

MAX_FILE_SIZE = 100_000  # 100 KB
DEFAULT_MAX_PROMPT_LENGTH = 10000

# ----------------------------
# Utility Functions
# ----------------------------

def is_virtual_env(directory: str) -> bool:
    """Checks if a directory is a Python virtual environment."""
    return os.path.exists(os.path.join(directory, "pyvenv.cfg"))

def trim_text(text: str, max_chars: int = DEFAULT_MAX_PROMPT_LENGTH) -> str:
    """Trims text to a specified max character limit."""
    return text[:max_chars] + "\n\n... (truncated)" if len(text) > max_chars else text

# ----------------------------
# File Summarization
# ----------------------------

def summarize_file(filepath: str, max_lines: int = 20) -> str:
    """Reads up to `max_lines` from a file to summarize its content."""
    lines = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as file:
            for _ in range(max_lines):
                line = file.readline()
                if not line:
                    break
                lines.append(line.rstrip())
        return trim_text("\n".join(lines))
    except Exception as e:
        return f"Error reading file: {e}"

# ----------------------------
# Python-Specific Analysis
# ----------------------------

def analyze_python_file(filepath: str) -> Dict[str, Union[List[str], str]]:
    """
    Uses AST to extract functions, classes, and imports from a Python file.
    Returns dictionary with keys: functions, classes, imports (or error).
    """
    analysis = {"functions": [], "classes": [], "imports": []}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                elif isinstance(node, ast.Import):
                    analysis["imports"].extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    analysis["imports"].append(node.module)
    except Exception as e:
        analysis["error"] = f"Error analyzing file: {e}"
    return analysis

# ----------------------------
# Directory Scanning
# ----------------------------

def get_directory_structure(root_dir: str) -> str:
    """Returns string representation of the directory tree, skipping ignored folders."""
    lines = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            d for d in dirnames
            if d not in IGNORE_FOLDERS and not is_virtual_env(os.path.join(dirpath, d))
        ]
        level = dirpath.replace(root_dir, "").count(os.sep)
        indent = " " * 4 * level
        lines.append(f"{indent}{os.path.basename(dirpath)}/")
        subindent = " " * 4 * (level + 1)
        for f in filenames:
            lines.append(f"{subindent}{f}")
    return trim_text("\n".join(lines))

def scan_repo(repo_path: str) -> Dict[str, Union[str, Dict]]:
    """
    Scans the repository and summarizes or analyzes each file.
    Python files are analyzed; others are summarized (up to size limit).
    """
    result = {}
    for dirpath, dirnames, filenames in os.walk(repo_path):
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
                    result[rel_path] = "File too large to process."
                elif ext == ".py":
                    result[rel_path] = analyze_python_file(full_path)
                else:
                    result[rel_path] = summarize_file(full_path)
            except Exception as e:
                result[rel_path] = f"Error processing file: {e}"
    return result

# ----------------------------
# Repository-Wide Utilities
# ----------------------------

def aggregate_imports(repo_analysis: Dict[str, Union[str, Dict]]) -> List[str]:
    """Returns a unique list of all Python imports found in the repo analysis."""
    imports = set()
    for data in repo_analysis.values():
        if isinstance(data, dict) and "imports" in data:
            imports.update(data.get("imports", []))
    return sorted(imports)

# ----------------------------
# Filtering
# ----------------------------

def filter_repo_analysis(
    repo_analysis: Dict[str, Union[str, Dict]],
    include_list: List[str] = None,
    exclude_list: List[str] = None
) -> Dict[str, Union[str, Dict]]:
    """
    Filters repo_analysis by include/exclude lists (wildcard support).
    Returns a filtered dictionary.
    """
    filtered = {}
    for path, data in repo_analysis.items():
        path_lower = path.lower()
        if exclude_list and any(fnmatch.fnmatch(path_lower, ex.lower()) for ex in exclude_list):
            continue
        if include_list and not any(fnmatch.fnmatch(path_lower, inc.lower()) for inc in include_list):
            continue
        filtered[path] = data
    return filtered

# ----------------------------
# Directory Tree Builder (from Analysis)
# ----------------------------

def build_directory_structure_from_analysis(repo_analysis: Dict[str, Union[str, Dict]]) -> str:
    """Builds a textual directory tree from keys in repo_analysis."""
    tree = {}

    for path in repo_analysis:
        parts = path.split(os.sep)
        node = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                node.setdefault("_files", []).append(part)
            else:
                node = node.setdefault(part, {})

    lines = []

    def build_lines(node: dict, indent: int = 0):
        for key in sorted(node.keys()):
            if key == "_files":
                for f in sorted(node[key]):
                    lines.append(" " * 4 * indent + f)
            else:
                lines.append(" " * 4 * indent + key + "/")
                build_lines(node[key], indent + 1)

    build_lines(tree)
    return "\n".join(lines)
