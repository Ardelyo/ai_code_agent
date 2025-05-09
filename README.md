# ✨ AI Code Agent ✨

<p align="center">
  <em>An intelligent command-line agent that understands your natural language requests to modify code blocks, leveraging Large Language Models for precise identification and generation.</em>
</p>

<p align="center">
  <a href="docs/en/tutorial.md">English Tutorial</a> |
  <a href="docs/id/tutorial.md">Tutorial Bahasa Indonesia</a> |
  <a href="docs/en/beginner-guide.md">Beginner's Guide</a>
</p>

## 🚀 Overview

The AI Code Agent is a powerful CLI tool designed to streamline code modifications. Instead of manually searching and editing code blocks, you can simply tell the agent what you want to change in plain English. It uses advanced Large Language Models (LLMs) like those accessible via OpenRouter or local models via Ollama to:

1. **Understand** your request
2. **Identify** the target file and the specific code block (function, class, or custom-marked region)
3. **Generate** the new code according to your instructions
4. **Preview** the changes and await your confirmation before applying them

## 🌟 Key Features

### Core AI Capabilities

* 🗣️ **Natural Language Understanding:** Accepts complex code modification requests in plain English
* 🎯 **Smart File Identification:** Automatically extracts target file paths from prompts or interactively asks for clarification
* 🔍 **AI-Powered Block Identification:** 
  * Targets functions, classes, or blocks defined by custom markers
  * Supports replacing definition lines or entire blocks
* ✍️ **AI-Powered Code Generation:** Generates contextually appropriate code based on your instructions

### Intelligent Code Replacement

* 🔄 **Precise Block Replacement:** Accurately locates and replaces identified code blocks
* 📏 **Smart Indentation Handling:** 
  * `match_original_block_start` (default): Aligns new code with original block's indent
  * `as_is`: Preserves existing indentation
* 🧩 **Empty Block Insertion:** Handles insertions between custom markers

### User Control & Safety

* 🔌 **Flexible LLM Backend:**
  * OpenRouter for accessing cutting-edge models
  * Ollama for local/offline use
* 🧐 **User Confirmation & Preview:**
  * Shows planned changes
  * Saves generated code for review
  * Requires explicit confirmation
* 🛡️ **Dry Run Mode:** Preview changes without modifying files
* 💾 **Automatic File Backups**

## 👨‍💻 Author & Credits

**Created by:**
- **Ardellio Satria Anindito**
  - Experience: 6 months
  - Portfolio: [bit.ly/ardelyo](https://bit.ly/ardelyo)
  - Instagram: [@ardel.yo](https://instagram.com/ardel.yo)
  - TikTok: [@ardel.yo](https://tiktok.com/@ardel.yo)

## ⚙️ Prerequisites

* Python 3.8+
* pip (Python package installer)
* (Optional) Ollama for local models

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone [YOUR_REPOSITORY_URL]
   cd ai-code-agent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Required packages:
   * pyyaml>=6.0
   * aiohttp>=3.8.0
   * aiofiles>=23.1.0

4. **Set up configuration:**
   ```bash
   cp config_agent.yaml.example config_agent.yaml
   ```
   Edit `config_agent.yaml` to add your API keys and preferred models.

## 📚 Documentation

- [English Documentation](docs/en/)
  - [Getting Started Guide](docs/en/getting-started.md)
  - [Tutorial](docs/en/tutorial.md)
  - [Beginner's Guide](docs/en/beginner-guide.md)
  - [Advanced Usage](docs/en/advanced-usage.md)
  - [API Reference](docs/en/api-reference.md)

- [Dokumentasi Bahasa Indonesia](docs/id/)
  - [Panduan Memulai](docs/id/getting-started.md)
  - [Tutorial](docs/id/tutorial.md)
  - [Panduan Pemula](docs/id/beginner-guide.md)
  - [Penggunaan Lanjutan](docs/id/advanced-usage.md)
  - [Referensi API](docs/id/api-reference.md)

## ▶️ Usage

```bash
python agent.py "Your natural language request to modify code" [options]
```

**Example:**
```bash
python agent.py "In utils.py, add a docstring to the 'calculate_sum' function explaining it takes two numbers and returns their sum."
```

### Command-Line Options

* `--file_path TEXT`: Manually specify target file path
* `--llm_provider [openrouter|ollama]`: Choose LLM provider
* `--model_identifier TEXT`: Specify model for block identification
* `--model_generation TEXT`: Specify model for code generation
* `--dry-run`: Show changes without modifying files
* `--no-backup`: Disable automatic file backups
* `--indentation_mode [match_original_block_start|as_is]`: Control indentation handling
* `--yes`: Auto-confirm prompts (use with caution!)

## 🛣️ Roadmap

* 🧠 Advanced planning with ReAct pattern
* 🗣️ Interactive clarification dialogs
* 🌳 AST-based code analysis
* 📂 Multi-file operations
* ✅ Automated testing integration
* 🛠️ Self-correction capabilities

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get involved.

1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

<p align="center">
  <em>Happy Coding (with a little AI help)! 🚀</em>
</p>