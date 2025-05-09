# Contributing to AI Code Agent

Thank you for considering contributing to AI Code Agent! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

1. **Fork the Repository**
   - Click the "Fork" button on GitHub
   - Clone your fork locally:
     ```bash
     git clone https://github.com/YOUR_USERNAME/ai-code-agent
     cd ai-code-agent
     ```

2. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**
   - Follow the coding style of the project
   - Add or update tests as needed
   - Update documentation if required

5. **Commit Your Changes**
   - Use clear and descriptive commit messages
   - Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
     ```bash
     feat: add new feature X
     fix: resolve issue with Y
     docs: update installation instructions
     ```

6. **Test Your Changes**
   - Ensure all tests pass
   - Run the agent with various test cases
   - Test both OpenRouter and Ollama configurations

7. **Submit a Pull Request**
   - Push to your fork
   - Submit a PR from your branch to our main branch
   - Describe your changes in detail
   - Link any related issues

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and modular

### Documentation

- Update relevant documentation for new features
- Document both English and Indonesian versions
- Include examples in tutorials when appropriate
- Keep the README.md up to date

### Testing

- Add tests for new features
- Update existing tests when modifying functionality
- Test edge cases and error conditions
- Verify both OpenRouter and Ollama integrations

### Commits and Pull Requests

- Keep commits focused and atomic
- Rebase your branch before submitting PR
- Squash related commits when appropriate
- Include tests and documentation in the same PR

## Project Structure

```
ai-code-agent/
├── agent.py            # Main agent logic
├── replacer_core.py    # Core code modification logic
├── connectors.py       # LLM API connectors
├── tools.py           # Utility tools and helpers
├── docs/              # Documentation
│   ├── en/            # English documentation
│   └── id/            # Indonesian documentation
└── tests/             # Test files
```

## Getting Help

- Check existing issues and discussions
- Join our community channels
- Read the documentation thoroughly
- Ask questions in GitHub Discussions

## Review Process

1. All PRs require at least one review
2. Address review comments promptly
3. Keep discussions focused and constructive
4. Be patient and respectful

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

Thank you for contributing to AI Code Agent! 🚀