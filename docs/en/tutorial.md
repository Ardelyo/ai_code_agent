# AI Code Agent Tutorial

This tutorial will walk you through real-world examples of using AI Code Agent, from basic to advanced use cases.

## Basic Examples

### 1. Adding Documentation
Let's start with a simple example of adding documentation to a function:

```python
# Original code in calc.py
def add(a, b):
    return a + b
```

Command:
```bash
python agent.py "Add a docstring to the add function in calc.py explaining it adds two numbers and returns their sum"
```

The agent will add proper documentation:
```python
def add(a, b):
    """
    Add two numbers together and return their sum.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        The sum of a and b
    """
    return a + b
```

### 2. Code Refactoring
Let's improve code readability:

```python
# Original code in data_processor.py
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result
```

Command:
```bash
python agent.py "Convert the for loop in process_data to use list comprehension"
```

The agent will refactor to:
```python
def process_data(items):
    return [item * 2 for item in items if item > 0]
```

## Intermediate Examples

### 1. Adding Error Handling
Adding robust error handling to existing code:

```python
# Original code in user_service.py
def get_user(user_id):
    data = database.query(f"SELECT * FROM users WHERE id = {user_id}")
    return data
```

Command:
```bash
python agent.py "Add proper error handling to get_user function including invalid ID and database connection errors"
```

The agent will enhance the code with proper error handling:
```python
def get_user(user_id):
    """
    Retrieve user data from the database.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        dict: User data if found

    Raises:
        ValueError: If user_id is invalid
        DatabaseError: If database connection fails
        UserNotFoundError: If user doesn't exist
    """
    try:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user ID")
        
        data = database.query(f"SELECT * FROM users WHERE id = %s", (user_id,))
        if not data:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return data
    except DatabaseError as e:
        logger.error(f"Database error while fetching user {user_id}: {e}")
        raise DatabaseError(f"Failed to retrieve user: {e}") from e
```

## Advanced Examples

### 1. Complex Refactoring
Converting a synchronous function to async:

Command:
```bash
python agent.py "Convert the fetch_user_data function to be async and use aiohttp instead of requests"
```

The agent will handle the complex transformation, including:
- Changing function signature
- Updating dependencies
- Converting to async/await syntax
- Maintaining error handling
- Updating related function calls

### 2. Adding New Features
Adding new functionality while maintaining existing code:

Command:
```bash
python agent.py "Add caching support to the get_weather function using Redis with 30-minute expiration"
```

The agent will:
1. Add Redis dependencies
2. Implement caching logic
3. Maintain existing error handling
4. Add cache invalidation

## Best Practices

1. **Start with Clear Goals**
   - Be specific about what you want to change
   - Mention file names when possible
   - Describe the desired outcome

2. **Review Changes**
   - Use `--dry-run` for complex changes
   - Check the generated code carefully
   - Verify error handling

3. **Iterative Development**
   - Make one change at a time
   - Test after each modification
   - Build up to complex changes

## Advanced Tips

1. **Using Multiple Files**
   ```bash
   python agent.py "Update all API endpoint functions in api/*.py to include rate limiting"
   ```

2. **Consistent Style**
   ```bash
   python agent.py "Format all functions in utils.py to follow PEP 8"
   ```

3. **Complex Patterns**
   ```bash
   python agent.py "Implement the observer pattern for the UserService class"
   ```

## What's Next?

- Explore [Advanced Usage](advanced-usage.md) for more complex scenarios
- Check out [API Reference](api-reference.md) for detailed command options
- Join our community to share your use cases and tips

Remember: The AI Code Agent is a powerful tool, but always review its output. It's designed to assist, not replace, your development expertise.