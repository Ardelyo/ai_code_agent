# Getting Started with AI Code Agent

Welcome to AI Code Agent! This guide will help you get up and running quickly with our intelligent code modification tool.

## Quick Start

1. **Prerequisites**
   - Python 3.8 or higher
   - pip package manager
   - (Optional) Ollama for local models

2. **Installation**
   ```bash
   git clone [YOUR_REPOSITORY_URL]
   cd ai-code-agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configuration**
   ```bash
   cp config_agent.yaml.example config_agent.yaml
   ```
   Edit `config_agent.yaml` with your preferred settings:
   ```yaml
   openrouter:
     api_key: "YOUR_API_KEY"
   ollama:
     base_url: "http://localhost:11434"
   ```

4. **First Command**
   ```bash
   python agent.py "Add a docstring to hello.py explaining what the greet function does"
   ```

## Basic Concepts

- **Natural Language Commands**: Just describe what you want to change in plain English
- **Smart File Detection**: The agent finds the right files automatically
- **Safe Operations**: Always previews changes and requires confirmation
- **Backup System**: Automatically backs up files before modifications

## Next Steps

- Check out our [Tutorial](tutorial.md) for more detailed examples
- Read the [Beginner's Guide](beginner-guide.md) for a deeper understanding
- Explore [Advanced Usage](advanced-usage.md) for power features

## Getting Help

If you run into any issues:
1. Check the error message for specific guidance
2. Review our [Troubleshooting Guide](troubleshooting.md)
3. Open an issue on our GitHub repository