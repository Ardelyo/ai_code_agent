# API Reference

This document provides detailed information about the AI Code Agent's command-line interface, configuration options, and programmatic API.

## Command Line Interface

### Basic Usage

```bash
python agent.py "<instruction>" [options]
```

### Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--file_path` | string | None | Specific file path to modify. Can use glob patterns. |
| `--llm_provider` | string | from config | LLM provider to use ('openrouter' or 'ollama'). |
| `--model_identifier` | string | from config | Model to use for code block identification. |
| `--model_generation` | string | from config | Model to use for code generation. |
| `--dry-run` | flag | False | Preview changes without applying them. |
| `--no-backup` | flag | False | Disable automatic file backups. |
| `--indentation_mode` | string | "match_original_block_start" | How to handle indentation ("match_original_block_start" or "as_is"). |
| `--yes` | flag | False | Skip confirmation prompts. |
| `--openrouter_api_key` | string | from config | OpenRouter API key. |
| `--ollama_base_url` | string | from config | Ollama base URL. |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | API key for OpenRouter |
| `OLLAMA_BASE_URL` | Base URL for Ollama API |
| `AI_CODE_AGENT_CONFIG` | Path to config file |

## Configuration File

The `config_agent.yaml` file supports the following configuration options:

```yaml
openrouter:
  api_key: string
  model_identifier: string
  model_generation: string

ollama:
  base_url: string
  model_identifier: string
  model_generation: string

default_provider: "openrouter" | "ollama"

backup:
  enabled: boolean
  max_backups: number
  path: string
  format: string

logging:
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR"
  file: string
  format: string

indentation:
  default_mode: "match_original_block_start" | "as_is"
```

### Configuration Details

#### OpenRouter Settings

```yaml
openrouter:
  api_key: "your_api_key"  # Required for OpenRouter
  model_identifier: "mistralai/mistral-7b-instruct"  # Default model for identification
  model_generation: "anthropic/claude-2"  # Default model for generation
```

#### Ollama Settings

```yaml
ollama:
  base_url: "http://localhost:11434"  # Default Ollama URL
  model_identifier: "codellama:13b"  # Default model for identification
  model_generation: "codellama:34b"  # Default model for generation
```

#### Backup Settings

```yaml
backup:
  enabled: true  # Enable/disable automatic backups
  max_backups: 5  # Maximum number of backup files to keep
  path: "./backups"  # Directory for backup files
  format: "{filename}.{timestamp}.bak"  # Backup filename format
```

#### Logging Settings

```yaml
logging:
  level: "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR)
  file: "ai_code_agent.log"  # Log file path
  format: "%(asctime)s - %(levelname)s - %(message)s"  # Log format
```

## Custom Block Markers

The agent supports custom block markers to define specific regions of code:

### Comment-based Markers

```python
# START_CUSTOM_LOGIC
def your_function():
    pass
# END_CUSTOM_LOGIC
```

### Region-based Markers (Multiple Languages)

```python
# region Custom Logic
def python_function():
    pass
# endregion
```

```csharp
#region Business Logic
public void CSharpMethod()
{
}
#endregion
```

```javascript
//#region API Routes
const router = express.Router();
//#endregion
```

## Error Handling

The agent provides detailed error messages and logging:

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| E001 | File not found | Check file path and permissions |
| E002 | Invalid configuration | Verify config_agent.yaml syntax |
| E003 | API authentication failed | Check API key configuration |
| E004 | Model not available | Verify model name or try alternative |
| E005 | Parse error | Check code block syntax |

### Error Recovery

The agent includes automatic error recovery mechanisms:

1. Automatic backup creation before modifications
2. Rollback on failed operations
3. Detailed error logging for debugging

## Integration API

For programmatic usage, the agent provides a Python API:

```python
from ai_code_agent import Agent, Config

# Initialize agent with custom configuration
agent = Agent(Config.from_file("config_agent.yaml"))

# Process a code modification request
result = agent.process_request(
    instruction="Add error handling to function",
    file_path="src/main.py",
    dry_run=True
)

# Get modification preview
preview = result.get_preview()

# Apply changes
if result.is_valid():
    result.apply()
```

### API Methods

| Method | Description |
|--------|-------------|
| `process_request()` | Process a modification request |
| `get_preview()` | Get preview of changes |
| `apply_changes()` | Apply modifications |
| `rollback()` | Revert changes |
| `validate()` | Validate proposed changes |

## Best Practices

### Configuration Management

1. Use environment variables for sensitive data
2. Version control your config_agent.yaml.example
3. Document custom configurations

### Error Handling

1. Always use `--dry-run` for critical changes
2. Enable logging for debugging
3. Maintain regular backups

### Performance Optimization

1. Use local models for rapid iteration
2. Batch similar changes
3. Optimize model selection for tasks

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify API keys
   - Check environment variables
   - Validate configuration file

2. **Model Errors**
   - Verify model availability
   - Check provider status
   - Try alternative models

3. **File Operations**
   - Check file permissions
   - Verify file paths
   - Ensure sufficient disk space

### Debug Mode

Enable debug logging for detailed information:

```yaml
logging:
  level: "DEBUG"
  file: "debug.log"
```

## Support

For additional help:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review [Common Issues](common-issues.md)
3. Open an issue on GitHub