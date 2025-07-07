# Amazon Bedrock Workshop Analysis Script

This script generates comprehensive summary documents for specified folders in the Amazon Bedrock Workshop using Amazon Bedrock's Converse API. It analyzes the content of each folder, including code, notebooks, and documentation, and generates a detailed summary with implementation details, architecture diagrams, key takeaways, and recommendations.

## Features

- **Folder Analysis**: Recursively analyzes folder content, including code, notebooks, and documentation
- **Configurable**: Uses YAML configuration for model selection, inference parameters, and output settings
- **Mermaid Diagrams**: Properly formats Mermaid diagrams for visual representation of architectures
- **Model Attribution**: Includes information about which model generated the summary and when
- **Flexible Execution**: Run for specific folders or all folders defined in the configuration

## Prerequisites

1. **AWS CLI configured** with access to Amazon Bedrock
2. **Python 3.7+** with the following packages:
   - boto3
   - pyyaml
3. **Amazon Bedrock access** with permissions to use the Converse API and the models specified in the configuration

## Setup

1. Ensure the script is in the `my-analysis` folder of the Amazon Bedrock Workshop repository
2. Configure your AWS credentials with access to Amazon Bedrock
3. Install required Python packages:
   ```bash
   pip install boto3 pyyaml
   ```

## Configuration

The script uses a YAML configuration file (`my-analysis/config.yml`) with the following structure:

```yaml
# Amazon Bedrock configuration
model:
  id: "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
  name: "Claude 3.7 Sonnet"
  provider: "Anthropic"

# Inference configuration
inference_config:
  temperature: 0.2
  max_tokens: 6000

# List of folders to analyze
folders_to_analyze:
  - "01_Text_generation"
  - "02_Knowledge_Bases_and_RAG"
  - "03_Model_customization"
  - "04_Image_and_Multimodal"
  - "05_Agents"
  - "06_OpenSource_examples"
  - "07_Cross_Region_Inference"

# Output configuration
output:
  directory: "my-analysis"
  file_prefix: "SUMMARY-"

# Debug configuration
debug:
  enabled: false  # Set to true to enable debug output
  print_prompt: true  # Print the full prompt sent to the model
```

### Configuration Options

- **model**: The Amazon Bedrock model to use for generating summaries
  - **id**: The model ID (ARN or alias)
  - **name**: A human-readable name for the model
  - **provider**: The model provider name
- **inference_config**: Parameters for the inference request
  - **temperature**: Controls randomness (0.0-1.0, lower is more deterministic)
  - **max_tokens**: Maximum number of tokens to generate
- **folders_to_analyze**: List of folders to analyze (relative to the repository root)
- **output**: Output configuration
  - **directory**: Directory to save the generated summaries
  - **file_prefix**: Prefix for the generated summary files
- **debug**: Debug configuration
  - **enabled**: Set to true to enable debug output
  - **print_prompt**: When true, prints information about the prompt sent to the model
- **file_selection**: Controls which files are included in the analysis
  - **max_notebooks**: Maximum number of notebooks to include (default: 3)
  - **max_notebook_cells**: Maximum cells per notebook to include (default: 5)
  - **max_python_files**: Maximum number of Python files to include (default: 3)
  - **max_python_lines**: Maximum lines per Python file to include (default: 50)
  - **max_markdown_files**: Maximum number of markdown files to include
  - **include_patterns**: List of glob patterns for files to always include (e.g., "main.py", "README*")
  - **exclude_patterns**: List of glob patterns for files to exclude (e.g., "__pycache__", "*.pyc")

## Usage

### Running the Script

You can run the script in several ways:

1. **Generate summaries for all folders defined in the config**:
   ```bash
   python my-analysis/generate_summaries.py
   ```

2. **Generate a summary for a specific folder**:
   ```bash
   python my-analysis/generate_summaries.py 03_Model_customization
   ```

3. **Generate summaries for multiple specific folders**:
   ```bash
   python my-analysis/generate_summaries.py 01_Text_generation 05_Agents
   ```

### Output

The script generates Markdown files with the following naming convention:
```
SUMMARY-{folder_name}.md
```

For example:
- `SUMMARY-01_Text_generation.md`
- `SUMMARY-02_Knowledge_Bases_and_RAG.md`

Each summary includes:
1. **Executive summary**: High-level overview of the module
2. **Implementation details breakdown**: Analysis of the code and implementation
3. **Key takeaways and lessons learned**: Important insights from the module
4. **Technical architecture overview**: Diagrams and explanations of the architecture
5. **Recommendations or next steps**: Suggestions for further exploration
6. **Model attribution**: Information about which model generated the summary and when

## Prompt Template

The script uses a prompt template from `my-analysis/prompts.md`. This template guides the LLM in generating the summary. You can modify this template to customize the output format or add specific instructions.

## Examples

### Example 1: Generate a summary for a single folder

```bash
python my-analysis/generate_summaries.py 01_Text_generation
```

This will generate `my-analysis/SUMMARY-01_Text_generation.md` with a comprehensive analysis of the Text Generation module.

### Example 2: Generate summaries for all folders

```bash
python my-analysis/generate_summaries.py
```

This will generate summary files for all folders listed in the `folders_to_analyze` section of the configuration file.

### Example 3: Change the model

1. Edit `my-analysis/config.yml`
2. Update the `model` section with the new model information
3. Run the script as usual

## Maximizing Context Window Usage

The script is optimized to make full use of Claude 3.7 Sonnet's 200K token context window, allowing for deeper and richer analysis of complex codebases:

1. **Dynamic Token Management**: The script tracks token usage and makes intelligent decisions about what content to include
2. **Prioritized Content**: Important files are always included first, followed by other files up to configured limits
3. **Token Budget**: Reserves only 2K tokens for prompt template and overhead, using up to 198K tokens for folder content
4. **Adaptive Truncation**: Automatically stops including content when approaching the token limit
5. **Markdown File Support**: Added support for including markdown documentation files

### Enhanced Configuration for Maximum Context Usage

```yaml
# File selection configuration
file_selection:
  max_notebooks: 150        # Increased from 5 to 150 (30x)
  max_notebook_cells: 300   # Increased from 10 to 300 (30x)
  max_python_files: 300     # Increased from 5 to 300 (60x)
  max_python_lines: 3000    # Increased from 100 to 3000 (30x)
  max_markdown_files: 150   # Increased from 5 to 150 (30x)
  include_patterns:         # Always include files matching these patterns
    - "main.py"
    - "*config*.py"
    - "README*"
    - "utils.py"
    - "*agent*.py"
    - "*model*.py"
    - "*data*.py"
    - "*util*.py"
    - "*helper*.py"
    - "*service*.py"
    - "*client*.py"
    - "*api*.py"
    - "requirements.txt"
  exclude_patterns:         # Skip files/directories matching these patterns
    - "__pycache__"
    - "*.pyc"
    - "venv/*"
    - "*.log"
    - "*.tmp"
    - "*.png"
    - "*.jpg"
    - "*.jpeg"
    - "*.gif"
    - "*.ico"
    - "*.svg"
    - "node_modules/*"
    - ".git/*"
```

### Token Usage Analysis

The script provides token usage information in the debug output:

```
DEBUG: Full prompt length: 202121 characters
DEBUG: Estimated token count: ~50530 tokens
```

This helps you understand how much of the context window is being used and adjust configuration as needed.

### Benefits of Maximized Context Window

1. **Deeper Analysis**: More code and documentation can be included in the prompt
2. **Better Understanding**: The LLM has more context to understand complex relationships
3. **More Comprehensive Summaries**: Generated summaries can cover more aspects of the codebase
4. **Richer Diagrams**: More context enables the LLM to create more detailed and accurate diagrams

## Troubleshooting

### Common Issues

1. **AWS Authentication Errors**:
   - Ensure your AWS credentials are properly configured
   - Verify you have access to Amazon Bedrock in the specified region

2. **Model Access Errors**:
   - Confirm you have access to the model specified in the configuration
   - Check if the model ID is correct and available in your region

3. **Output Formatting Issues**:
   - If Mermaid diagrams aren't rendering correctly, check for syntax errors in the generated markdown
   - Adjust the `clean_model_response` function in the script if needed

4. **Memory or Timeout Errors**:
   - For large folders, you might need to increase the timeout settings
   - Consider analyzing fewer folders at once

### Logs and Debugging

The script outputs progress information to the console, including:
- Which folder is being analyzed
- When a summary is successfully generated
- Any errors that occur during execution

#### Debug Mode

To enable debug mode and see more detailed information:

1. Edit the `config.yml` file
2. Set `debug.enabled` to `true`
3. Run the script as usual

Debug mode will show:
- The length of the full prompt sent to the model
- The estimated token count of the prompt
- The first and last 500 characters of the prompt in the console
- The entire prompt saved to a debug log file (`debug_[folder_name].log`) in the my-analysis folder
- This can be helpful for troubleshooting issues with the prompt or understanding why the model generates certain responses

Example debug output:
```
================================================================================
DEBUG: Full prompt length: 202121 characters
DEBUG: Estimated token count: ~50530 tokens
DEBUG: First 500 characters of prompt:
# Amazon Bedrock Workshop Module Analysis Prompt

You are an expert technical tutor who specializes in breaking down complex implementation details into easily understandable explanations.

## Task
Analyze and document the codebase in the folder 06_OpenSource_examples and create a comprehensive summary.

## Deliverables

### Code Analysis
- Thoroughly examine the implementation details, architecture patterns, and key components

### Summary Document
Create a well-structured file named SUMMARY-06...

DEBUG: Last 500 characters of prompt:
... tool is used to check which destinations user has already traveled.
        If user has already been to a city then do not recommend that city.
    
        Returns:
            str: Destination to be recommended.
    
        """
    
        df = read_travel_data()
        user_id = config.get("configurable", {}).get("user_id")

        if user_id not in df["Id"].values:
            return "User not found in the travel database."
================================================================================
```

## Contributing

To contribute to this script:
1. Fork the repository
2. Make your changes
3. Submit a pull request with a clear description of the improvements

## License

This script is released under the same license as the Amazon Bedrock Workshop repository.
