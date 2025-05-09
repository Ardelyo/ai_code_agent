# Advanced Usage Guide

This guide covers advanced features and techniques for getting the most out of AI Code Agent.

## Advanced Features

### Working with Multiple Files

The agent can handle complex operations across multiple files:

```bash
# Update related functions across files
python agent.py "Update the login system to use JWT tokens instead of session cookies" --dry-run

# Refactor shared components
python agent.py "Extract common utility functions from api/*.py into a new utils/api_helpers.py module"
```

### Custom Block Markers

Use custom markers to define specific code regions:

```python
# START_CUSTOM_LOGIC
def complex_business_logic():
    # your code here
# END_CUSTOM_LOGIC
```

Then modify only that section:
```bash
python agent.py "Optimize the code between START_CUSTOM_LOGIC and END_CUSTOM_LOGIC markers"
```

### LLM Provider Configuration

#### OpenRouter Setup
For access to state-of-the-art models:

```yaml
openrouter:
  api_key: "your_key"
  model_identifier: "mistralai/mistral-7b-instruct"
  model_generation: "anthropic/claude-2"
```

#### Ollama Setup
For local, private model execution:

```yaml
ollama:
  base_url: "http://localhost:11434"
  model_identifier: "codellama:13b"
  model_generation: "codellama:34b"
```

### Advanced CLI Options

```bash
# Combine multiple options
python agent.py "Refactor user authentication" \
  --file_path src/auth.py \
  --llm_provider ollama \
  --model_generation "codellama:34b" \
  --dry-run

# Process multiple files
python agent.py "Add input validation" \
  --file_path "src/api/*.py" \
  --yes
```

## Advanced Use Cases

### 1. Complex Refactoring

#### Converting to Design Patterns
```bash
# Convert to Factory Pattern
python agent.py "Refactor DocumentProcessor class to use the Factory pattern for different document types"

# Implement Observer Pattern
python agent.py "Add observer pattern to UserService to notify dependent services of user changes"
```

#### Architectural Changes
```bash
# Switch to Hexagonal Architecture
python agent.py "Restructure the order processing system to follow hexagonal architecture principles"
```

### 2. Performance Optimization

#### Caching Implementation
```bash
# Add Redis Caching
python agent.py "Add Redis caching to expensive database queries in UserRepository"

# Implement Memoization
python agent.py "Add memoization to recursive functions in algorithm.py"
```

#### Async Conversion
```bash
# Convert to Async
python agent.py "Convert synchronous file operations in storage.py to use aiofiles"
```

### 3. Testing Enhancement

#### Adding Test Coverage
```bash
# Generate Tests
python agent.py "Generate comprehensive unit tests for the OrderProcessor class"

# Add Property-Based Tests
python agent.py "Add hypothesis-based property tests for the data validation functions"
```

## Best Practices for Advanced Usage

### 1. Complex Changes Strategy

1. **Break Down Changes**
   ```bash
   # Step 1: Extract interface
   python agent.py "Extract interface from UserService class"
   
   # Step 2: Create implementation
   python agent.py "Create MongoDB implementation of UserService interface"
   
   # Step 3: Update dependencies
   python agent.py "Update service references to use UserService interface"
   ```

2. **Use Dry Runs**
   ```bash
   # Preview complex changes
   python agent.py "Implement CQRS pattern for order processing" --dry-run
   ```

### 2. Working with Large Codebases

1. **Scope Control**
   ```bash
   # Limit to specific modules
   python agent.py "Update logging" --file_path "src/logging/*.py"
   ```

2. **Incremental Changes**
   ```bash
   # Phase 1
   python agent.py "Convert User class to use dataclass, keeping existing methods"
   
   # Phase 2
   python agent.py "Add validation to User dataclass fields"
   ```

### 3. Custom Workflows

1. **Combining with Git**
   ```bash
   # Create feature branch
   git checkout -b feature/new-auth
   
   # Make changes
   python agent.py "Implement OAuth2 authentication"
   
   # Review and commit
   git add .
   git commit -m "feat: implement OAuth2 authentication"
   ```

2. **CI/CD Integration**
   ```bash
   # Update GitHub Actions
   python agent.py "Add type checking step to CI pipeline in .github/workflows/ci.yml"
   ```

## Advanced Configuration

### Custom Backup Strategy
```yaml
backup:
  enabled: true
  max_backups: 5
  path: "./backups"
  format: "{filename}.{timestamp}.bak"
```

### Logging Configuration
```yaml
logging:
  level: "DEBUG"
  file: "ai_code_agent.log"
  format: "%(asctime)s - %(levelname)s - %(message)s"
```

## Troubleshooting Advanced Issues

1. **Model Selection Issues**
   - Try different models for different tasks
   - Use larger models for complex refactoring
   - Use specialized code models for framework-specific tasks

2. **Performance Optimization**
   - Use local models for faster iterations
   - Batch similar changes together
   - Utilize parallel processing features

3. **Complex Codebase Navigation**
   - Use custom markers for complex sections
   - Break down large files
   - Maintain consistent code structure

## What's Next?

- Contribute to the project
- Share your advanced use cases
- Join the developer community
- Explore integration possibilities

Remember: With great power comes great responsibility. Always review generated changes, especially for complex modifications.