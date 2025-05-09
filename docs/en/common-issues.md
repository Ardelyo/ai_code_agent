# Common Issues

This document lists frequently encountered issues and their solutions when using AI Code Agent.

## Model-Related Issues

### 1. Model Not Responding

**Problem**: Model takes too long to respond or times out.

**Solutions**:
- Try a different model (e.g., switch from OpenRouter to Ollama)
- Use a smaller, faster model for simpler tasks
- Check your internet connection
- Increase timeout settings in configuration

### 2. Poor Code Generation

**Problem**: Generated code is incorrect or low quality.

**Solutions**:
- Be more specific in your instructions
- Provide more context in your prompts
- Try a different model that specializes in code
- Break down complex changes into smaller steps

### 3. Model Not Available

**Problem**: Selected model cannot be accessed.

**Solutions**:
- Verify model name in configuration
- Check if you have access to the model
- Ensure API key has necessary permissions
- Try an alternative model

## File Operations

### 1. File Not Found

**Problem**: Agent cannot find the target file.

**Solutions**:
- Check file path is correct
- Verify file exists in the workspace
- Use absolute paths if needed
- Check file permissions

### 2. File Modification Failed

**Problem**: Changes cannot be applied to file.

**Solutions**:
- Ensure file is not read-only
- Check file is not open in another program
- Verify sufficient disk space
- Check file system permissions
- Use `--dry-run` to test changes first

### 3. Backup Issues

**Problem**: Cannot create backup files.

**Solutions**:
- Check disk space
- Verify backup directory permissions
- Clean up old backups
- Configure backup location in config_agent.yaml

## Configuration Problems

### 1. Invalid Configuration

**Problem**: Configuration file cannot be loaded.

**Solutions**:
- Verify YAML syntax
- Check file encoding (use UTF-8)
- Compare with config_agent.yaml.example
- Remove problematic settings

### 2. API Key Issues

**Problem**: API authentication fails.

**Solutions**:
- Check API key is valid
- Verify key is properly configured
- Ensure key has not expired
- Check for environment variable conflicts

### 3. Model Configuration

**Problem**: Model settings are incorrect.

**Solutions**:
- Verify model names/identifiers
- Check provider-specific settings
- Update to latest model versions
- Use recommended model configurations

## Code Block Identification

### 1. Block Not Found

**Problem**: Agent cannot find the target code block.

**Solutions**:
- Be more specific in block description
- Check if block exists in file
- Use proper function/class names
- Try using custom markers

### 2. Wrong Block Selected

**Problem**: Agent modifies wrong code section.

**Solutions**:
- Use more specific identifiers
- Add custom markers around target block
- Preview changes with `--dry-run`
- Break down complex files

### 3. Marker Issues

**Problem**: Custom markers not working.

**Solutions**:
- Check marker syntax
- Verify marker placement
- Use unique marker names
- Follow marker format guidelines

## Performance Issues

### 1. Slow Operation

**Problem**: Agent operations are too slow.

**Solutions**:
- Use local models via Ollama
- Work with smaller files
- Split large changes
- Optimize model selection

### 2. Memory Usage

**Problem**: High memory consumption.

**Solutions**:
- Process smaller files
- Use more efficient models
- Clean up old backups
- Monitor system resources

### 3. Rate Limiting

**Problem**: API rate limits reached.

**Solutions**:
- Use local models when possible
- Implement request throttling
- Batch similar changes
- Upgrade API plan if needed

## Best Practices to Avoid Issues

1. **Always Test First**
   - Use `--dry-run` for preview
   - Test on sample files
   - Review changes carefully

2. **Maintain Good Structure**
   - Keep files organized
   - Use consistent naming
   - Document code properly

3. **Regular Maintenance**
   - Update dependencies
   - Clean up backups
   - Monitor disk space
   - Keep configuration updated

4. **Proper Configuration**
   - Use secure API keys
   - Configure logging
   - Set appropriate timeouts
   - Document custom settings

## Getting More Help

If you encounter issues not covered here:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review the [API Reference](api-reference.md)
3. Search GitHub issues
4. Join community discussions
5. Create a detailed bug report

Remember to always include:
- Error messages
- Configuration details
- Steps to reproduce
- System information