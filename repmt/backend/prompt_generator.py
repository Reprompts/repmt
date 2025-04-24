# Copyright (c) 2025 RePromptsQuest
# Licensed under the MIT License

import os
from .backend import trim_text, DEFAULT_MAX_PROMPT_LENGTH, filter_repo_analysis, build_directory_structure_from_analysis, aggregate_imports

def generate_readme_prompt(repo_structure, repo_analysis, max_prompt_length=DEFAULT_MAX_PROMPT_LENGTH, include_list=None, exclude_list=None):
    """
    Generates a standardized README.md prompt.
    """
    filtered_analysis = filter_repo_analysis(repo_analysis, include_list, exclude_list)
    filtered_structure = build_directory_structure_from_analysis(filtered_analysis) if filtered_analysis else repo_structure
    imports = aggregate_imports(filtered_analysis)
    prompt = (
        "Generate a well-structured README.md for the following repository. Include:\n"
        "- A clear summary of the project's purpose\n"
        "- Installation instructions\n"
        "- Usage examples\n"
        "- A breakdown of each major component with descriptions\n\n"
        "The repository has the following directory structure (excluding virtual environments and dependency folders):\n\n"
        f"{filtered_structure}\n\n"
        "The project uses these libraries:\n" + ", ".join(imports) + "\n\n"
        "Tokenize key function and class names in each module where applicable."
    )
    return trim_text(prompt, max_chars=max_prompt_length)

def generate_overview_prompt(repo_structure, repo_analysis, max_prompt_length=DEFAULT_MAX_PROMPT_LENGTH, include_list=None, exclude_list=None):
    """
    Generates a repository overview prompt that instructs a step-by-step explanation of the repo.
    The overview should include a hierarchical directory structure where each module is annotated
    with its important imports, functions, and classes.
    """
    filtered_analysis = filter_repo_analysis(repo_analysis, include_list, exclude_list)
    filtered_structure = build_directory_structure_from_analysis(filtered_analysis) if filtered_analysis else repo_structure
    
    detailed_lines = []
    for path, analysis in filtered_analysis.items():
        indent = " " * (path.count(os.sep) * 4)
        line = f"{indent}{path}"
        if isinstance(analysis, dict):
            funcs = ", ".join(analysis.get("functions", []))
            classes = ", ".join(analysis.get("classes", []))
            imports = ", ".join(analysis.get("imports", []))
            details = " | ".join(filter(None, [
                f"Functions: {funcs}" if funcs else "",
                f"Classes: {classes}" if classes else "",
                f"Imports: {imports}" if imports else ""
            ]))
            line += f"  -> {details}"
        else:
            line += f"  -> {analysis}"
        detailed_lines.append(line)
    
    detailed_structure = "\n".join(detailed_lines)
    
    prompt = (
        "Provide a comprehensive, step-by-step overview of the repository. Your explanation should include:\n"
        "1. A hierarchical directory structure that shows the layout of the project.\n"
        "2. For each module or file, annotate the following details:\n"
        "   - Key imports (libraries or modules used)\n"
        "   - Important functions defined\n"
        "   - Classes that are present\n"
        "3. Describe the purpose of each module and how it fits into the overall architecture.\n\n"
        "Use the following detailed structure as your guide:\n\n"
        f"{detailed_structure}\n\n"
        "Ensure that every part of the repository is clearly explained in logical, sequential steps."
    )
    return trim_text(prompt, max_chars=max_prompt_length)

def generate_flow_prompt(repo_structure, repo_analysis, max_prompt_length=DEFAULT_MAX_PROMPT_LENGTH, include_list=None, exclude_list=None):
    """
    Generates a prompt for creating a detailed flowchart of the repository's code flow.
    The prompt instructs to provide both a visual flowchart and a step-by-step, tabular explanation of the module interactions,
    including the important modules/dependencies as well as functions and classes defined in each module.
    """
    filtered_analysis = filter_repo_analysis(repo_analysis, include_list, exclude_list)
    filtered_structure = build_directory_structure_from_analysis(filtered_analysis) if filtered_analysis else repo_structure
    
    detailed_lines = []
    for path, analysis in filtered_analysis.items():
        indent = " " * (path.count(os.sep) * 4)
        line = f"{indent}{path}"
        if isinstance(analysis, dict):
            funcs = ", ".join(analysis.get("functions", []))
            classes = ", ".join(analysis.get("classes", []))
            imports = ", ".join(analysis.get("imports", []))
            details = " | ".join(filter(None, [
                f"Functions: {funcs}" if funcs else "",
                f"Classes: {classes}" if classes else "",
                f"Imports: {imports}" if imports else ""
            ]))
            line += f"  -> {details}"
        else:
            line += f"  -> {analysis}"
        detailed_lines.append(line)
    
    detailed_structure = "\n".join(detailed_lines)
    prompt = (
        "Generate a comprehensive flowchart for the repository's code flow. Your output should include the following:\n\n"
        "1. A visual flowchart diagram that maps out how the modules interact and the sequence of operations, "
        "following the hierarchical directory structure provided below.\n\n"
        "2. A detailed, step-by-step table that explains the flow of execution. The table should include:\n"
        "   - The module or file name\n"
        "   - The key functions and classes defined in that module\n"
        "   - The main imports and dependencies that affect the flow\n"
        "   - A brief description of the operations performed and how data flows between modules\n\n"
        "3. A summary of important modules and external dependencies (e.g., libraries installed via pip) used across the repository.\n\n"
        "Use the annotated directory structure below as your guide:\n\n"
        f"{filtered_structure}\n\n"
        f"{detailed_structure}\n\n"
        "Ensure that your response clearly indicates the flow between modules, the role of each dependency, and provides a logical, sequential breakdown of the repository's operations."
    )

    return trim_text(prompt, max_chars=max_prompt_length)

def generate_structure_prompt(repo_structure, repo_analysis, max_prompt_length=DEFAULT_MAX_PROMPT_LENGTH, include_list=None, exclude_list=None):
    """
    Generates a detailed repository structure documentation prompt including:
    - Module hierarchy with key components
    - Function/class definitions
    - Critical dependencies
    - Module interaction patterns
    """
    filtered_analysis = filter_repo_analysis(repo_analysis, include_list, exclude_list)
    filtered_structure = build_directory_structure_from_analysis(filtered_analysis) if filtered_analysis else repo_structure
    
    # Build detailed module component listing
    module_details = []
    for path, analysis in filtered_analysis.items():
        if isinstance(analysis, dict):
            details = {
                "path": path,
                "functions": analysis.get("functions", []),
                "classes": analysis.get("classes", []),
                "imports": [imp for imp in analysis.get("imports", []) 
                           if not imp.startswith(('.', '/'))]  # Filter local imports
            }
            module_details.append(details)
    
    # Format the detailed components
    detail_sections = []
    for detail in module_details:
        section = f"Module: {detail['path']}\n"
        if detail['functions']:
            section += f"- Functions: {', '.join(detail['functions'])}\n"
        if detail['classes']:
            section += f"- Classes: {', '.join(detail['classes'])}\n"
        if detail['imports']:
            section += f"- External Dependencies: {', '.join(detail['imports'])}\n"
        detail_sections.append(section)
    
    prompt = (
        "Generate comprehensive documentation of the repository structure with:\n\n"
        "1. Hierarchical Module Overview:\n"
        f"{filtered_structure}\n\n"
        "2. Detailed Module Breakdown (per file):\n"
        f"{chr(10).join(detail_sections)}\n\n"
        "3. Structure Analysis covering:\n"
        "- Purpose and responsibilities of each major module\n"
        "- Key architectural patterns in the directory structure\n"
        "- Notable external dependencies and their usage contexts\n"
        "- Important module-to-module relationships\n\n"
        "Format the output with clear section headers and consistent formatting "
        "suitable for technical documentation."
    )

    return trim_text(prompt, max_chars=max_prompt_length)

def generate_module_prompt(selected_modules, repo_structure, repo_analysis, max_prompt_length=DEFAULT_MAX_PROMPT_LENGTH, exclude_list=None):
    """
    Generates detailed prompts for specific modules with:
    - Complete module/file hierarchy
    - All functions and classes
    - Internal and external dependencies
    - Usage context within the repository
    """
    filtered_analysis = filter_repo_analysis(repo_analysis, include_list=selected_modules, exclude_list=exclude_list)
    filtered_structure = build_directory_structure_from_analysis(filtered_analysis) if filtered_analysis else repo_structure
    
    # Build comprehensive module documentation
    module_docs = []
    for module_path, analysis in filtered_analysis.items():
        if isinstance(analysis, dict):
            doc = {
                "path": module_path,
                "functions": analysis.get("functions", []),
                "classes": analysis.get("classes", []),
                "imports": analysis.get("imports", []),
                "external_deps": [imp for imp in analysis.get("imports", []) 
                                 if not any(imp.startswith(x) for x in ('.', '/', 'reprompt'))]
            }
            module_docs.append(doc)
    
    # Format the prompt sections
    prompt_sections = []
    for doc in module_docs:
        section = f"## Module: {doc['path']}\n"
        if doc['functions']:
            section += f"### Functions:\n- " + "\n- ".join(doc['functions']) + "\n"
        if doc['classes']:
            section += f"### Classes:\n- " + "\n- ".join([f"{cls} (methods: {', '.join(methods) if isinstance(methods, dict) else 'N/A'})" 
                                                       for cls, methods in doc['classes'].items()]) + "\n"
        if doc['imports']:
            section += f"### Dependencies:\n- Internal: {', '.join([i for i in doc['imports'] if i.startswith('reprompt')]) or 'None'}\n"
            section += f"- External: {', '.join(doc['external_deps']) or 'None'}\n"
        prompt_sections.append(section)
    
    prompt = (
        "Generate comprehensive documentation for the selected modules with:\n\n"
        "1. Module Purpose:\n"
        "- Clear explanation of each module's role\n"
        "- Key responsibilities and features\n\n"
        "2. Technical Specifications:\n"
        f"{chr(10).join(prompt_sections)}\n\n"
        "3. Integration Details:\n"
        "- How this module interacts with others\n"
        "- Data flow in/out of the module\n"
        "- Important architectural considerations\n\n"
        "4. Usage Examples:\n"
        "- Typical calling patterns\n"
        "- Common configuration scenarios\n\n"
        "Refer to the repository structure for context:\n"
        f"{filtered_structure}\n\n"
        "Format with clear Markdown headings and bullet points."
    )
    
    return trim_text(prompt, max_chars=max_prompt_length)


def generate_issue_search_prompt(repo_structure, repo_analysis, issue_description, max_prompt_length=DEFAULT_MAX_PROMPT_LENGTH):
    """
    Generates a prompt to help locate where an issue might exist in the repository.
    Includes detailed directory structure and module information.
    """
    detailed_lines = []
    for path, analysis in repo_analysis.items():
        indent = " " * (path.count(os.sep) * 4)
        line = f"{indent}{path}"
        if isinstance(analysis, dict):
            funcs = ", ".join(analysis.get("functions", []))
            classes = ", ".join(analysis.get("classes", []))
            imports = ", ".join(analysis.get("imports", []))
            details = " | ".join(filter(None, [
                f"Functions: {funcs}" if funcs else "",
                f"Classes: {classes}" if classes else "",
                f"Imports: {imports}" if imports else ""
            ]))
            line += f"  -> {details}"
        else:
            line += f"  -> {analysis}"
        detailed_lines.append(line)
    
    detailed_structure = "\n".join(detailed_lines)
    
    prompt = (
        f"I'm experiencing this issue: '{issue_description}'\n\n"
        "Based on the repository structure and module details below, help me identify:\n"
        "1. Which files/modules are most likely related to this issue\n"
        "2. Potential causes based on the code structure\n"
        "3. Where to look first for debugging\n\n"
        "Repository Structure:\n"
        f"{repo_structure}\n\n"
        "Detailed Module Information:\n"
        f"{detailed_structure}\n\n"
        "Provide your analysis in this format:\n"
        "1. Most Relevant Files: [list files]\n"
        "2. Potential Causes: [brief analysis]\n"
        "3. Debugging Steps: [suggested actions]"
    )
    return trim_text(prompt, max_chars=max_prompt_length)