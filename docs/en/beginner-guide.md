# Beginner's Guide to AI Code Agent

This guide is designed to help newcomers understand and effectively use the AI Code Agent. We'll walk through basic concepts and provide plenty of examples.

## Understanding How It Works

The AI Code Agent works in four simple steps:

1. **You make a request** in plain English
2. **AI understands and plans** the changes
3. **Changes are previewed** for your review
4. **You confirm** and changes are applied

## Common Use Cases

### 1. Adding Documentation
```bash
python agent.py "Add docstrings to all functions in utils.py"
```

### 2. Fixing Simple Bugs
```bash
python agent.py "Fix the off-by-one error in the range loop in process_list function"
```

### 3. Adding New Features
```bash
python agent.py "Add input validation to the calculate_age function to ensure date is not in the future"
```

### 4. Code Refactoring
```bash
python agent.py "Convert the for loop in parse_data to use list comprehension"
```

## Best Practices

1. **Be Specific**
   - Good: "Add parameter type hints to the process_user function in auth.py"
   - Less Good: "Add some type hints somewhere"

2. **Start Small**
   - Make smaller, focused changes first
   - Build up to more complex modifications

3. **Review Changes**
   - Always check the preview
   - Use `--dry-run` for complex changes

4. **Use Safety Features**
   - Don't disable automatic backups unless necessary
   - Keep your config file secure

## Common Parameters

- `--dry-run`: Preview changes without applying them
- `--file_path`: Specify exact file to modify
- `--no-backup`: Disable automatic backups (use carefully!)
- `--yes`: Skip confirmation (use carefully!)

## Tips for Success

1. **Clear Instructions**
   - Mention specific file names when known
   - Describe the desired outcome, not just the problem

2. **Understanding Context**
   - The agent can see the whole file
   - It understands code structure and patterns

3. **Interactive Usage**
   - Start with simple changes
   - Build confidence gradually

## What's Next?

- Try the examples in our [Tutorial](tutorial.md)
- Explore [Advanced Usage](advanced-usage.md)
- Check out real-world examples in our [Case Studies](case-studies.md)

Remember: The AI Code Agent is a tool to assist you, not replace your judgment. Always review changes before applying them!