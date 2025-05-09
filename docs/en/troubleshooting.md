# Troubleshooting Guide

This guide helps you resolve common issues you might encounter while using AI Code Agent.

## Common Issues and Solutions

### Installation Issues

#### Python Environment Problems

**Issue**: ImportError or ModuleNotFoundError
```
ImportError: No module named 'yaml'
```

**Solution**:
1. Ensure you're in the correct virtual environment
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Reinstall dependencies
   ```bash
   pip install -r requirements.txt
   ```

#### Configuration Issues

**Issue**: Configuration file not found
```
FileNotFoundError: config_agent.yaml not found
```

**Solution**:
1. Copy the example configuration
   ```bash
   cp config_agent.yaml.example config_agent.yaml
   ```
2. Edit config_agent.yaml with your settings

### API Connection Issues

#### OpenRouter Issues

**Issue**: Authentication failed
```
ERROR: OpenRouter API authentication failed
```

**Solutions**:
1. Verify your API key in config_agent.yaml
2. Check if the API key is set in environment variables
3. Ensure the API key has sufficient permissions

#### Ollama Issues

**Issue**: Cannot connect to Ollama
```
ConnectionError: Failed to connect to http://localhost:11434
```

**Solutions**:
1. Ensure Ollama is running
2. Verify the base URL in configuration
3. Check if Ollama is accessible from your network

### Code Modification Issues

#### File Access Problems

**Issue**: Permission denied
```
PermissionError: [Errno 13] Permission denied: 'file.py'
```

**Solutions**:
1. Check file permissions
2. Run the command with appropriate privileges
3. Ensure the file isn't open in another program

#### Backup Issues

**Issue**: Cannot create backup
```
ERROR: Failed to create backup file
```

**Solutions**:
1. Check disk space
2. Verify backup directory permissions
3. Clean up old backups using:
   ```bash
   python agent.py --cleanup-backups
   ```

### Model-Related Issues

#### Model Loading Problems

**Issue**: Model not available
```
ERROR: Model 'model_name' not found
```

**Solutions**:
1. Verify model name in configuration
2. Check if the model is available in your provider
3. Try an alternative model

#### Generation Issues

**Issue**: Timeout during code generation
```
ERROR: Request timed out after 60 seconds
```

**Solutions**:
1. Try a smaller code block
2. Use a local model via Ollama
3. Increase timeout in configuration

## Advanced Troubleshooting

### Debug Mode

Enable debug logging for detailed information:

```yaml
logging:
  level: "DEBUG"
  file: "debug.log"
```

### Log Analysis

Common log patterns and their meanings:

1. **Block Identification Failures**
   ```
   DEBUG: Failed to identify code block in file.py
   ```
   - Check if the target code exists
   - Verify file contents
   - Use more specific instructions

2. **Model Response Issues**
   ```
   DEBUG: Invalid model response format
   ```
   - Try a different model
   - Simplify the request
   - Check model configuration

3. **File Operation Errors**
   ```
   DEBUG: Failed to apply changes to file.py
   ```
   - Check file permissions
   - Verify file path
   - Ensure sufficient disk space

### Recovery Steps

If something goes wrong:

1. **Check Backups**
   - Look in the backup directory
   - Restore from backup if needed
   - Verify file integrity

2. **Reset Configuration**
   ```bash
   cp config_agent.yaml.example config_agent.yaml
   ```

3. **Clean Environment**
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Performance Optimization

### Slow Operations

If operations are slow:

1. **Use Local Models**
   - Configure Ollama
   - Use smaller models
   - Cache frequently used operations

2. **Optimize File Operations**
   - Work with smaller files
   - Use specific file paths
   - Batch similar changes

3. **Network Issues**
   - Check internet connection
   - Use cached models when possible
   - Configure appropriate timeouts

## Getting Help

If you're still experiencing issues:

1. **Check Documentation**
   - Review this troubleshooting guide
   - Check the [API Reference](api-reference.md)
   - Read the [Advanced Usage](advanced-usage.md) guide

2. **Community Support**
   - Search existing issues on GitHub
   - Check community discussions
   - Share minimal reproducible examples

3. **Report Bugs**
   - Include error messages
   - Provide configuration details
   - Share steps to reproduce

## Prevention Tips

1. **Regular Maintenance**
   - Keep dependencies updated
   - Clean old backups
   - Monitor disk space

2. **Best Practices**
   - Use version control
   - Make incremental changes
   - Test changes in isolation

3. **Configuration Management**
   - Keep sensitive data secure
   - Document custom settings
   - Maintain backup configurations

Remember: Always use `--dry-run` for critical changes and maintain backups of important files.