#!/usr/bin/env python3
"""
Script to generate comprehensive summary documents for specified folders in the Amazon Bedrock Workshop
using Amazon Bedrock's Converse API with the prompt template from prompts.md.
Configuration is loaded from config.yml.
"""

import os
import sys
import json
import boto3
import time
import yaml
import re
import fnmatch
from pathlib import Path
from datetime import datetime

# Configuration paths
REPO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANALYSIS_DIR = REPO_ROOT / "my-analysis"
PROMPT_TEMPLATE_PATH = ANALYSIS_DIR / "prompts.md"
CONFIG_PATH = ANALYSIS_DIR / "config.yml"

def load_config():
    """Load configuration from YAML file."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading configuration from {CONFIG_PATH}: {e}")
        return None

def read_file(file_path):
    """Read the contents of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def list_files(directory):
    """List all files in a directory recursively."""
    result = []
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                result.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
    return result

def filter_files(files, config):
    """Filter files based on include and exclude patterns."""
    # Get patterns from config or use defaults
    include_patterns = config.get('file_selection', {}).get('include_patterns', [])
    exclude_patterns = config.get('file_selection', {}).get('exclude_patterns', [])
    
    # Start with files that match include patterns
    important_files = []
    for file_path in files:
        file_name = os.path.basename(file_path)
        for pattern in include_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                important_files.append(file_path)
                break
    
    # Filter out excluded files
    filtered_files = []
    for file_path in files:
        file_name = os.path.basename(file_path)
        exclude_match = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_name, pattern):
                exclude_match = True
                break
        if not exclude_match and file_path not in important_files:
            filtered_files.append(file_path)
    
    return important_files, filtered_files

def get_folder_content_summary(folder_name, config=None):
    """Get a summary of the folder's content to provide context to the LLM."""
    if config is None:
        config = {}
    
    print(f"  - Reading files from {folder_name}...")
    
    folder_path = REPO_ROOT / folder_name
    if not folder_path.exists():
        print(f"Folder {folder_name} does not exist.")
        return None
    
    # Read README.md if it exists
    readme_path = folder_path / "README.md"
    readme_content = read_file(readme_path) if readme_path.exists() else "No README.md found."
    
    # Get all files in the folder
    all_files = list_files(folder_path)
    total_files = len(all_files)
    
    # Apply smart file selection
    important_files, filtered_files = filter_files(all_files, config)
    
    # Get file selection limits from config - set to very high values to effectively consume entire files
    max_notebooks = config.get('file_selection', {}).get('max_notebooks', 1000)
    max_notebook_cells = config.get('file_selection', {}).get('max_notebook_cells', 10000)
    max_python_files = config.get('file_selection', {}).get('max_python_files', 1000)
    max_python_lines = config.get('file_selection', {}).get('max_python_lines', 100000)
    max_markdown_files = config.get('file_selection', {}).get('max_markdown_files', 1000)
    
    # Calculate estimated token budget (200K tokens max, reserve 10K for prompt template and other overhead)
    max_tokens = 190000
    estimated_tokens_used = 0
    
    # Combine important files with filtered files, prioritizing important ones
    selected_files = important_files + filtered_files
    
    # Categorize files
    notebooks = [f for f in selected_files if f.endswith('.ipynb')]
    python_files = [f for f in selected_files if f.endswith('.py')]
    markdown_files = [f for f in selected_files if f.endswith('.md')]
    yaml_files = [f for f in selected_files if f.endswith('.yaml') or f.endswith('.yml')]
    terraform_files = [f for f in selected_files if f.endswith('.tf')]
    shell_files = [f for f in selected_files if f.endswith('.sh')]
    text_files = [f for f in selected_files if f.endswith('.txt')]
    other_files = [f for f in selected_files if not (f.endswith('.ipynb') or f.endswith('.py') or f.endswith('.md') or 
                                                    f.endswith('.yaml') or f.endswith('.yml') or f.endswith('.tf') or 
                                                    f.endswith('.sh') or f.endswith('.txt'))]
    
    # Create a summary of the folder content
    content_summary = f"# Folder Content Summary for {folder_name}\n\n"
    content_summary += "## README Content\n\n"
    content_summary += readme_content + "\n\n"
    
    # Add file statistics
    content_summary += f"## File Statistics\n\n"
    content_summary += f"Total files found: {total_files}\n"
    content_summary += f"Notebooks: {len([f for f in all_files if f.endswith('.ipynb')])}\n"
    content_summary += f"Python files: {len([f for f in all_files if f.endswith('.py')])}\n"
    content_summary += f"Markdown files: {len([f for f in all_files if f.endswith('.md')])}\n"
    content_summary += f"YAML files: {len([f for f in all_files if f.endswith('.yaml') or f.endswith('.yml')])}\n"
    content_summary += f"Terraform files: {len([f for f in all_files if f.endswith('.tf')])}\n"
    content_summary += f"Shell script files: {len([f for f in all_files if f.endswith('.sh')])}\n"
    content_summary += f"Text files: {len([f for f in all_files if f.endswith('.txt')])}\n"
    content_summary += f"Other files: {len([f for f in all_files if not (f.endswith('.ipynb') or f.endswith('.py') or 
                                                                        f.endswith('.md') or f.endswith('.yaml') or 
                                                                        f.endswith('.yml') or f.endswith('.tf') or 
                                                                        f.endswith('.sh') or f.endswith('.txt'))])}\n\n"
    
    if len(important_files) > 0:
        content_summary += f"Important files selected based on patterns: {len(important_files)}\n\n"
    
    # Add all file types to the analysis count
    max_yaml_files = config.get('file_selection', {}).get('max_yaml_files', 1000)
    max_terraform_files = config.get('file_selection', {}).get('max_terraform_files', 1000)
    max_shell_files = config.get('file_selection', {}).get('max_shell_files', 1000)
    max_text_files = config.get('file_selection', {}).get('max_text_files', 1000)
    
    files_analyzed = (len(notebooks[:max_notebooks]) + len(python_files[:max_python_files]) + 
                     len(markdown_files[:max_markdown_files]) + len(yaml_files[:max_yaml_files]) +
                     len(terraform_files[:max_terraform_files]) + len(shell_files[:max_shell_files]) +
                     len(text_files[:max_text_files]))
    
    # Only show warning if we're actually skipping files
    if files_analyzed < total_files:
        content_summary += f"**Note: Analyzing {files_analyzed} out of {total_files} files.**\n\n"
        
    # Add list of skipped files if any
    skipped_files = []
    if len(notebooks) > max_notebooks:
        skipped_files.extend([os.path.basename(f) for f in notebooks[max_notebooks:]])
    if len(python_files) > max_python_files:
        skipped_files.extend([os.path.basename(f) for f in python_files[max_python_files:]])
    if len(markdown_files) > max_markdown_files:
        skipped_files.extend([os.path.basename(f) for f in markdown_files[max_markdown_files:]])
    if len(yaml_files) > max_yaml_files:
        skipped_files.extend([os.path.basename(f) for f in yaml_files[max_yaml_files:]])
    
    if skipped_files:
        content_summary += "**Skipped files:**\n"
        for skipped_file in skipped_files[:20]:  # Show up to 20 skipped files
            content_summary += f"- {skipped_file}\n"
        if len(skipped_files) > 20:
            content_summary += f"- ... and {len(skipped_files) - 20} more files\n"
        content_summary += "\n"
    
    content_summary += "## Files in the folder\n\n"
    
    if notebooks:
        content_summary += "### Notebooks\n"
        for notebook in [os.path.basename(f) for f in notebooks]:
            content_summary += f"- {notebook}\n"
        content_summary += "\n"
    
    if python_files:
        content_summary += "### Python Files\n"
        for py_file in [os.path.basename(f) for f in python_files]:
            content_summary += f"- {py_file}\n"
        content_summary += "\n"
    
    if markdown_files:
        content_summary += "### Markdown Files\n"
        for md_file in [os.path.basename(f) for f in markdown_files]:
            if md_file != "README.md":  # Skip README as it's already included
                content_summary += f"- {md_file}\n"
        content_summary += "\n"
        
    if yaml_files:
        content_summary += "### YAML Files\n"
        for yaml_file in [os.path.basename(f) for f in yaml_files]:
            content_summary += f"- {yaml_file}\n"
        content_summary += "\n"
        
    if terraform_files:
        content_summary += "### Terraform Files\n"
        for tf_file in [os.path.basename(f) for f in terraform_files]:
            content_summary += f"- {tf_file}\n"
        content_summary += "\n"
        
    if shell_files:
        content_summary += "### Shell Script Files\n"
        for sh_file in [os.path.basename(f) for f in shell_files]:
            content_summary += f"- {sh_file}\n"
        content_summary += "\n"
        
    if text_files:
        content_summary += "### Text Files\n"
        for txt_file in [os.path.basename(f) for f in text_files]:
            content_summary += f"- {txt_file}\n"
        content_summary += "\n"
    
    if other_files:
        content_summary += "### Other Files\n"
        for other_file in [os.path.basename(f) for f in other_files][:20]:  # Limit to 20 other files
            content_summary += f"- {other_file}\n"
        if len(other_files) > 20:
            content_summary += f"- ... and {len(other_files) - 20} more files\n"
        content_summary += "\n"
    
    # Add content of key files
    content_summary += "## Content of Key Files\n\n"
    
    # Prioritize important files for content inclusion
    notebook_paths = [f for f in important_files if f.endswith('.ipynb')] + [f for f in filtered_files if f.endswith('.ipynb')]
    python_paths = [f for f in important_files if f.endswith('.py')] + [f for f in filtered_files if f.endswith('.py')]
    markdown_paths = [f for f in important_files if f.endswith('.md')] + [f for f in filtered_files if f.endswith('.md')]
    terraform_paths = [f for f in important_files if f.endswith('.tf')] + [f for f in filtered_files if f.endswith('.tf')]
    shell_paths = [f for f in important_files if f.endswith('.sh')] + [f for f in filtered_files if f.endswith('.sh')]
    text_paths = [f for f in important_files if f.endswith('.txt')] + [f for f in filtered_files if f.endswith('.txt')]
    
    # Track token usage (rough estimation)
    tokens_used = len(content_summary) // 4
    
    # Add content of notebooks
    for notebook_path in notebook_paths[:max_notebooks]:
        notebook_content = read_file(notebook_path)
        if notebook_content:
            notebook_header = f"### {os.path.basename(notebook_path)}\n\n"
            content_summary += notebook_header
            tokens_used += len(notebook_header) // 4
            
            # Try to extract markdown cells or code cells from the notebook
            try:
                notebook_json = json.loads(notebook_content)
                cells_to_include = min(max_notebook_cells, len(notebook_json.get('cells', [])))
                
                for cell in notebook_json.get('cells', [])[:cells_to_include]:
                    if cell.get('cell_type') == 'markdown':
                        cell_content = ''.join(cell.get('source', []))
                        cell_tokens = len(cell_content) // 4
                        
                        # Check if adding this cell would exceed token budget
                        if tokens_used + cell_tokens > max_tokens:
                            content_summary += "*Note: Remaining cells omitted due to token limit*\n\n"
                            break
                            
                        content_summary += f"{cell_content}\n\n"
                        tokens_used += cell_tokens
                        
                    elif cell.get('cell_type') == 'code':
                        cell_content = ''.join(cell.get('source', []))
                        code_block = f"```python\n{cell_content}\n```\n\n"
                        code_tokens = len(code_block) // 4
                        
                        # Check if adding this code would exceed token budget
                        if tokens_used + code_tokens > max_tokens:
                            content_summary += "*Note: Remaining cells omitted due to token limit*\n\n"
                            break
                            
                        content_summary += code_block
                        tokens_used += code_tokens
                
                # We're consuming entire files, so no need for this note
            except:
                error_msg = "Could not parse notebook content.\n\n"
                content_summary += error_msg
                tokens_used += len(error_msg) // 4
    
    # Add content of Python files
    for py_path in python_paths[:max_python_files]:
        # Check if we're approaching token limit
        if tokens_used > max_tokens * 0.9:
            content_summary += "*Note: Additional files omitted due to token limit*\n\n"
            break
            
        py_content = read_file(py_path)
        if py_content:
            file_header = f"### {os.path.basename(py_path)}\n\n"
            content_summary += file_header
            tokens_used += len(file_header) // 4
            
            # Limit to configured number of lines
            py_lines = py_content.split('\n')
            lines_to_include = min(max_python_lines, len(py_lines))
            
            code_block = f"```python\n{'\n'.join(py_lines[:lines_to_include])}\n```\n\n"
            code_tokens = len(code_block) // 4
            
            # Check if adding this code would exceed token budget
            if tokens_used + code_tokens > max_tokens:
                content_summary += "*Note: File content omitted due to token limit*\n\n"
            else:
                content_summary += code_block
                tokens_used += code_tokens
                
                # We're consuming entire files, so no need for this note
    
    # Add content of markdown files (excluding README.md which is already included)
    for md_path in markdown_paths[:max_markdown_files]:
        # Skip README.md as it's already included
        if os.path.basename(md_path) == "README.md":
            continue
            
        # Check if we're approaching token limit
        if tokens_used > max_tokens * 0.95:
            content_summary += "*Note: Additional markdown files omitted due to token limit*\n\n"
            break
            
        md_content = read_file(md_path)
        if md_content:
            file_header = f"### {os.path.basename(md_path)}\n\n"
            content_summary += file_header
            tokens_used += len(file_header) // 4
            
            # Add the markdown content directly
            content_summary += f"{md_content}\n\n"
            tokens_used += len(md_content) // 4
            
    # Add content of YAML files - set to very high values to effectively consume entire files
    max_yaml_files = config.get('file_selection', {}).get('max_yaml_files', 1000)
    max_yaml_lines = config.get('file_selection', {}).get('max_yaml_lines', 100000)
    max_terraform_files = config.get('file_selection', {}).get('max_terraform_files', 1000)
    max_terraform_lines = config.get('file_selection', {}).get('max_terraform_lines', 100000)
    max_shell_files = config.get('file_selection', {}).get('max_shell_files', 1000)
    max_shell_lines = config.get('file_selection', {}).get('max_shell_lines', 100000)
    max_text_files = config.get('file_selection', {}).get('max_text_files', 1000)
    max_text_lines = config.get('file_selection', {}).get('max_text_lines', 100000)
    
    # Prioritize important YAML files for content inclusion
    yaml_paths = [f for f in important_files if f.endswith('.yaml') or f.endswith('.yml')] + [f for f in filtered_files if f.endswith('.yaml') or f.endswith('.yml')]
    
    for yaml_path in yaml_paths[:max_yaml_files]:
        # Check if we're approaching token limit
        if tokens_used > max_tokens * 0.9:
            content_summary += "*Note: Additional YAML files omitted due to token limit*\n\n"
            break
            
        yaml_content = read_file(yaml_path)
        if yaml_content:
            file_header = f"### {os.path.basename(yaml_path)}\n\n"
            content_summary += file_header
            tokens_used += len(file_header) // 4
            
            # Limit to configured number of lines
            yaml_lines = yaml_content.split('\n')
            lines_to_include = min(max_yaml_lines, len(yaml_lines))
            
            code_block = f"```yaml\n{'\n'.join(yaml_lines[:lines_to_include])}\n```\n\n"
            code_tokens = len(code_block) // 4
            
            # Check if adding this code would exceed token budget
            if tokens_used + code_tokens > max_tokens:
                content_summary += "*Note: File content omitted due to token limit*\n\n"
            else:
                content_summary += code_block
                tokens_used += code_tokens
                
                # We're consuming entire files, so no need for this note
    
    # Add content of Terraform files
    for tf_path in terraform_paths[:max_terraform_files]:
        # Check if we're approaching token limit
        if tokens_used > max_tokens * 0.9:
            content_summary += "*Note: Additional files omitted due to token limit*\n\n"
            break
            
        tf_content = read_file(tf_path)
        if tf_content:
            file_header = f"### {os.path.basename(tf_path)}\n\n"
            content_summary += file_header
            tokens_used += len(file_header) // 4
            
            # Limit to configured number of lines
            tf_lines = tf_content.split('\n')
            lines_to_include = min(max_terraform_lines, len(tf_lines))
            
            code_block = f"```hcl\n{'\n'.join(tf_lines[:lines_to_include])}\n```\n\n"
            code_tokens = len(code_block) // 4
            
            # Check if adding this code would exceed token budget
            if tokens_used + code_tokens > max_tokens:
                content_summary += "*Note: File content omitted due to token limit*\n\n"
            else:
                content_summary += code_block
                tokens_used += code_tokens
    
    # Add content of Shell script files
    for sh_path in shell_paths[:max_shell_files]:
        # Check if we're approaching token limit
        if tokens_used > max_tokens * 0.9:
            content_summary += "*Note: Additional files omitted due to token limit*\n\n"
            break
            
        sh_content = read_file(sh_path)
        if sh_content:
            file_header = f"### {os.path.basename(sh_path)}\n\n"
            content_summary += file_header
            tokens_used += len(file_header) // 4
            
            # Limit to configured number of lines
            sh_lines = sh_content.split('\n')
            lines_to_include = min(max_shell_lines, len(sh_lines))
            
            code_block = f"```bash\n{'\n'.join(sh_lines[:lines_to_include])}\n```\n\n"
            code_tokens = len(code_block) // 4
            
            # Check if adding this code would exceed token budget
            if tokens_used + code_tokens > max_tokens:
                content_summary += "*Note: File content omitted due to token limit*\n\n"
            else:
                content_summary += code_block
                tokens_used += code_tokens
    
    # Add content of Text files
    for txt_path in text_paths[:max_text_files]:
        # Check if we're approaching token limit
        if tokens_used > max_tokens * 0.9:
            content_summary += "*Note: Additional files omitted due to token limit*\n\n"
            break
            
        txt_content = read_file(txt_path)
        if txt_content:
            file_header = f"### {os.path.basename(txt_path)}\n\n"
            content_summary += file_header
            tokens_used += len(file_header) // 4
            
            # Limit to configured number of lines
            txt_lines = txt_content.split('\n')
            lines_to_include = min(max_text_lines, len(txt_lines))
            
            code_block = f"```\n{'\n'.join(txt_lines[:lines_to_include])}\n```\n\n"
            code_tokens = len(code_block) // 4
            
            # Check if adding this code would exceed token budget
            if tokens_used + code_tokens > max_tokens:
                content_summary += "*Note: File content omitted due to token limit*\n\n"
            else:
                content_summary += code_block
                tokens_used += code_tokens
                    
    # Add token usage information
    # content_summary += f"\n## Token Usage Information\n\n"
    # content_summary += f"- Estimated tokens used in this content summary: ~{tokens_used} tokens\n"
    # content_summary += f"- Token budget allocated: {max_tokens} tokens\n"
    # content_summary += f"- Percentage of budget used: {(tokens_used / max_tokens) * 100:.1f}%\n\n"
    
    return content_summary

def generate_summary_with_bedrock(folder_name, prompt_template, config):
    """Generate a summary for a folder using Amazon Bedrock's Converse API."""
    print(f"Analyzing folder: {folder_name}")
    
    # Get folder content summary
    folder_content = get_folder_content_summary(folder_name, config)
    if not folder_content:
        return None
    
    # Clean folder name for report file name
    clean_folder_name = folder_name.split('_')[0] if '_' in folder_name else folder_name
    report_file_name = f"{config['output']['file_prefix']}{clean_folder_name}"
    
    # Create the complete report filename
    complete_report_filename = f"{config['output']['file_prefix']}{folder_name}.md"
    
    # Replace placeholders in the prompt template
    prompt = prompt_template.replace('[codebase-folder-name]', folder_name)
    prompt = prompt.replace('[report-file-name]', complete_report_filename)
    prompt = prompt.replace('[report-folder-name]', config['output']['directory'])
    
    # Add specific instructions to avoid preamble and use the correct title
    prompt += f"\n\nIMPORTANT: Start your response directly with the title '# {complete_report_filename}' (not abbreviated). Do not include any introductory text, preamble, or markdown tags before the title. Begin with the exact title and proceed with the analysis."
    
    # Create the full prompt with folder content
    full_prompt = f"{prompt}\n\n# Folder Content to Analyze\n\n{folder_content}"
    
    # Check if debug mode is enabled
    debug_enabled = config.get('debug', {}).get('enabled', False)
    print_prompt = config.get('debug', {}).get('print_prompt', False)
    
    if debug_enabled and print_prompt:
        # Estimate token count (rough approximation: 1 token ≈ 4 characters for English text)
        estimated_tokens = len(full_prompt) // 4
        
        # Comment out verbose prompt printing to console
        # print(f"\n{'='*80}")
        print(f"DEBUG: Full prompt length: {len(full_prompt)} characters")
        print(f"DEBUG: Estimated token count: ~{estimated_tokens} tokens")
        # print(f"DEBUG: First 500 characters of prompt:\n{full_prompt[:500]}...\n")
        # print(f"DEBUG: Last 500 characters of prompt:\n...{full_prompt[-500:]}\n{'='*80}\n")
        
        # Create logs directory if it doesn't exist
        logs_dir = ANALYSIS_DIR / "logs"
        os.makedirs(logs_dir, exist_ok=True)
        
        # Save the entire prompt to a debug log file in the logs subfolder
        # Replace slashes with underscores for the log filename to avoid directory issues
        safe_folder_name = folder_name.replace('/', '_')
        debug_log_path = logs_dir / f"debug_{safe_folder_name}.log"
        with open(debug_log_path, 'w', encoding='utf-8') as log_file:
            log_file.write(f"# Debug Log for {folder_name}\n")
            log_file.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}\n")
            log_file.write(f"# Prompt length: {len(full_prompt)} characters\n")
            log_file.write(f"# Estimated token count: ~{estimated_tokens} tokens\n\n")
            log_file.write("# FULL PROMPT:\n\n")
            log_file.write(full_prompt)
            log_file.write("\n\n# END OF PROMPT")
        
        print(f"DEBUG: Full prompt saved to {debug_log_path}")

    # Initialize Bedrock client
    session = boto3.session.Session()
    region = session.region_name
    bedrock = boto3.client(service_name='bedrock-runtime', region_name=region)
    
    try:
        print(f"  - Calling Bedrock API with {config['model']['name']}...")
        # Call Amazon Bedrock Converse API
        response = bedrock.converse(
            modelId=config['model']['id'],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ],
            inferenceConfig={
                "temperature": config['inference_config']['temperature'],
                "maxTokens": config['inference_config']['max_tokens']
            }
        )
        
        # Extract the model's response
        model_response = response["output"]["message"]["content"][0]["text"]
        
        print(f"  - Processing model response...")
        # Clean up the response by removing preamble and markdown tags
        model_response = clean_model_response(model_response)
        
        # Add token utilization summary and model information to the response
        # estimated_tokens = len(full_prompt) // 4
        # token_info = f"\n\n## Token Utilization Summary\n\n"
        # token_info += f"- **Prompt Length**: {len(full_prompt)} characters\n"
        # token_info += f"- **Estimated Token Count**: ~{estimated_tokens} tokens\n"
        # token_info += f"- **Context Window Utilization**: ~{(estimated_tokens / 200000) * 100:.1f}% of 200K token context window\n"
        
        # model_info = f"\n\n---\n\n*This summary was generated by {config['model']['name']} from {config['model']['provider']} on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}.*"
        # model_response += token_info + model_info
        
        return model_response
    
    except Exception as e:
        print(f"Error calling Amazon Bedrock: {str(e)}")
        return None

def clean_model_response(response):
    """Clean up the model response by removing preamble and markdown tags."""
    # Remove any text before the first heading
    if "# SUMMARY" in response:
        response = response[response.find("# SUMMARY"):]
    
    # Remove any introductory text that might still be present
    lines = response.split('\n')
    start_index = 0
    for i, line in enumerate(lines):
        if line.startswith("# SUMMARY"):
            start_index = i
            break
    
    response = '\n'.join(lines[start_index:])
    
    # Fix Mermaid diagram formatting
    # First, remove any standalone backtick blocks that might interfere
    response = re.sub(r'```\s*```', '', response)
    
    # Special handling for mermaid diagrams with multiple subgraphs
    # This pattern looks for mermaid diagrams that might be incorrectly split
    pattern = r'```mermaid\n(.*?)\n```\s*\n\s*subgraph'
    while re.search(pattern, response, re.DOTALL):
        response = re.sub(pattern, r'```mermaid\n\1\n    subgraph', response, flags=re.DOTALL)
    
    # Find all instances of "mermaid" followed by diagram types
    response = re.sub(r'(\n|^)mermaid\s*\n(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|gantt|pie|journey|gitGraph|mindmap|timeline|sankey|requirement|erDiagram)', 
                     r'\1```mermaid\n\2', response)
    
    # Fix standalone subgraph blocks that should be part of a mermaid diagram
    lines = response.split('\n')
    result = []
    in_mermaid = False
    pending_subgraph = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for mermaid block start
        if line == '```mermaid':
            in_mermaid = True
            result.append(lines[i])
        
        # Check for mermaid block end
        elif line == '```' and in_mermaid:
            # Check if the next non-empty line is a subgraph
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            
            if j < len(lines) and lines[j].strip().startswith('subgraph'):
                # Don't end the mermaid block yet, skip this closing backtick
                pass
            else:
                # Normal end of mermaid block
                in_mermaid = False
                result.append(lines[i])
        
        # Check for standalone subgraph that should be part of a mermaid diagram
        elif line.startswith('subgraph') and not in_mermaid:
            # Look back to see if there was a mermaid block that just ended
            if result and result[-1].strip() == '```':
                # Remove the last closing backtick
                result.pop()
                in_mermaid = True
            else:
                # Start a new mermaid block
                result.append('```mermaid')
                in_mermaid = True
            
            # Add the subgraph line with proper indentation
            result.append('    ' + lines[i])
        
        # Inside mermaid block
        elif in_mermaid:
            # Add proper indentation to subgraph content
            if line.startswith('subgraph') or line == 'end' or line.startswith('    '):
                result.append(lines[i])
            else:
                result.append('    ' + lines[i])
        
        # Normal line outside mermaid block
        else:
            result.append(lines[i])
        
        i += 1
    
    # Ensure the last mermaid block is closed if it's still open
    if in_mermaid:
        result.append('```')
    
    return '\n'.join(result)

def generate_summary_file(folder_name, prompt_template, config):
    """Generate a summary file for a folder using Amazon Bedrock."""
    # Create output filename using the full folder name, replacing slashes with underscores
    safe_folder_name = folder_name.replace('/', '_')
    output_file = ANALYSIS_DIR / f"{config['output']['file_prefix']}{safe_folder_name}.md"
    
    # Skip if the summary file already exists
    if output_file.exists():
        print(f"\nSkipping folder: {folder_name} (summary already exists)")
        return True
    
    print(f"\nProcessing folder: {folder_name}")
    summary = generate_summary_with_bedrock(folder_name, prompt_template, config)
    if summary:
        print(f"  - Saving summary to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✓ Summary generated: {output_file}")
        return True
    return False

def main():
    """Main function to generate summaries for specified folders."""
    # Create output directory if it doesn't exist
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    
    # Load configuration
    config = load_config()
    if not config:
        print("Error: Could not load configuration. Exiting.")
        return
    
    # Read the prompt template
    prompt_template = read_file(PROMPT_TEMPLATE_PATH)
    if not prompt_template:
        print(f"Error: Could not read prompt template from {PROMPT_TEMPLATE_PATH}")
        return
    
    # Process command line arguments if provided, otherwise use default list from config
    folders = sys.argv[1:] if len(sys.argv) > 1 else config['folders_to_analyze']
    
    # Filter out any None or empty values that might come from commented lines in YAML
    if not sys.argv[1:]:  # Only filter if using config file
        folders = [folder for folder in folders if folder]
    
    print(f"DEBUG: Loaded folders from config: {config['folders_to_analyze']}")
    print(f"DEBUG: Final folders list after filtering: {folders}")
    print(f"\nGenerating summaries for {len(folders)} folders using {config['model']['name']}...")
    print("=" * 80)
    
    success_count = 0
    for folder in folders:
        if generate_summary_file(folder, prompt_template, config):
            success_count += 1
            # Add a small delay between API calls to avoid rate limiting
            time.sleep(5)
    
    print("=" * 80)
    print(f"\nSummary generation complete. {success_count}/{len(folders)} summaries generated.")

if __name__ == "__main__":
    main()
