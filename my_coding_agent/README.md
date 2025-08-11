# 🤖 CodeBuddy - Your Intelligent Development Companion

A comprehensive, AI-powered coding assistant that combines file management, code execution, Git operations, security analysis, and quality assessment in one powerful CLI tool.

## ✨ Features

### 🔧 **Core Capabilities**
- **26 Integrated Tools** spanning file operations, code execution, Git workflows, analysis, and code generation
- **Real-time LLM Integration** with Google Gemini API and intelligent fallback modes
- **Beautiful CLI Interface** with rich formatting, colors, and intuitive commands
- **Comprehensive Safety System** with risk assessment and user approval workflows

### 📁 **File & Folder Operations**
- **Smart File Management**: Read, write, create, and delete files with syntax highlighting
- **Directory Operations**: Create and manage folders with safety protections
- **Intelligent Content Generation**: AI-powered file creation with contextual content

### 🐍 **Code Execution & Analysis**
- **Python Execution**: Run Python files with output capture and error handling
- **Shell Command Execution**: Secure command execution with safety approval system
- **Syntax Validation**: Real-time Python syntax checking and validation

### 🔍 **Advanced Code Analysis**
- **Python Linting**: Style checking, best practices, and code quality assessment
- **Complexity Analysis**: Cyclomatic complexity, function metrics, and quality scoring
- **Security Scanning**: Vulnerability detection for injection attacks, hardcoded secrets, and dangerous functions
- **Dependency Analysis**: Project dependency scanning and risk assessment
- **Comprehensive Quality Reports**: Combined analysis with actionable recommendations

### 🌿 **Git Integration**
- **Repository Management**: Status checking, diff viewing, and commit history
- **Branch Operations**: Create, switch, delete, and list branches
- **Remote Operations**: Push and pull with intelligent risk assessment
- **Staging & Commits**: File staging and commit management with message validation

### ✨ **Code Writing & Generation**
- **AI Code Generation**: Convert natural language descriptions into working Python code
- **Professional Templates**: 10+ code templates for scripts, modules, tests, configs, and more
- **Smart Refactoring**: Automated code improvement with function extraction, naming, and documentation
- **Code Snippets**: Common design patterns, algorithms, and utility functions on demand
- **Multi-Format Support**: Generate calculators, web scrapers, APIs, Flask apps, CLI tools, and databases

### 🛡️ **Safety & Security**
- **5-Level Risk Assessment**: SAFE, LOW, MEDIUM, HIGH, CRITICAL classifications
- **Smart Approval System**: Context-aware safety prompts with detailed warnings
- **Operation Protection**: Prevents destructive actions without explicit user consent
- **Security-First Design**: Built-in protections against common vulnerabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key (optional - falls back to mock mode)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Kaushik-2005/CodeBuddy.git
   cd my_coding_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment** (optional):
   ```bash
   # Create .env file with your Gemini API key
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

4. **Run the agent**:
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### Basic Commands

#### File Operations
```bash
# Read files
show me main.py
show me config.json

# Create files
create calculator.py with basic math functions
create README.md with project documentation

# Manage directories
create folder tests
delete old_file.py  # Requires approval
```

#### Code Execution
```bash
# Run Python files
run calculator.py
run tests/test_suite.py

# Execute shell commands (with approval)
run command "pip install requests"
run command "ls -la"

# Check syntax
check syntax main.py
```

#### Git Operations
```bash
# Repository status
git status
git log 10

# File staging and commits
git add main.py
git commit "Add new feature"

# Branch management
git branch                    # List branches
git branch create feature-x  # Create branch
git branch switch main       # Switch branch

# Remote operations (require approval)
git push origin main
git pull origin develop
```

#### Code Analysis
```bash
# Quality analysis
lint main.py                  # Style and quality check
analyze complexity main.py    # Complexity metrics
security scan main.py        # Security vulnerability scan
analyze dependencies         # Project dependency analysis
code quality main.py         # Comprehensive quality report
```

#### Code Writing & Generation
```bash
# AI Code Generation
generate calculator code                    # Generate to console
generate web scraper to scraper.py        # Generate to file
generate flask app with database          # Complex application

# Professional Templates
code template python_script               # Basic Python script
code template test_file                   # Unit test template
code template dockerfile                  # Docker configuration

# Code Refactoring
refactor code main.py                     # Auto-improve code
refactor code utils.py with add_docstrings # Add documentation
refactor code app.py with extract_functions # Extract functions

# Code Snippets
code snippet singleton                    # Design pattern
code snippet file_reader                 # Common utility
code snippet decorator                   # Python decorator
```

### Advanced Features

#### Safety Approval System
The agent automatically assesses operation risk and requests approval for potentially dangerous actions:

- **🟢 SAFE**: Executes immediately (file reading, Git status)
- **🔵 LOW**: Simple confirmation (file creation, Git add)
- **🟡 MEDIUM**: Detailed approval (Git push to feature branches)
- **🟠 HIGH**: Strong warnings (Git push to main, file deletion)
- **🔴 CRITICAL**: Maximum protection (destructive commands)

#### Example Approval Flow
```bash
🤖 CodeBuddy: git push origin main

⚠️  HIGH RISK OPERATION
Operation: Push to origin/main
Warnings:
• ⚠️  This operation affects important files/directories
• ⚠️  This action cannot be easily undone

Do you want to proceed with this high operation? (y/N):
```

## 🏗️ Architecture

### Project Structure
```
my_coding_agent/
├── main.py                 # Entry point and agent orchestration
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env                   # Environment variables (optional)
│
├── core/                  # Core agent functionality
│   ├── agent.py          # Main agent logic and tool coordination
│   ├── llm_client.py     # LLM integration (Gemini API + mock mode)
│   └── memory.py         # Agent memory and learning system
│
├── interface/             # User interface components
│   └── cli.py            # Rich CLI with formatting and interactions
│
├── tools/                 # Tool implementations
│   ├── base_tool.py      # Base tool interface and registry
│   ├── file_ops.py       # File and folder operations
│   ├── code_ops.py       # Code execution and syntax checking
│   ├── git_tools.py      # Git operations and workflows
│   ├── analysis_tools.py # Code analysis (linting, complexity)
│   └── security_tools.py # Security scanning and dependency analysis
│
├── safety/                # Safety and approval system
│   └── approval.py       # Risk assessment and user approval workflows
│
└── tests/                 # Test files and debugging utilities
    ├── test_*.py         # Comprehensive test suites
    ├── debug_*.py        # Debugging and development tools
    └── sample_files/     # Test files for analysis
```

### Core Components

#### 🧠 **Agent Core** (`core/agent.py`)
- **Tool Orchestration**: Manages 22 integrated tools
- **Request Processing**: Natural language to tool command translation
- **Safety Integration**: Automatic risk assessment and approval workflows
- **Memory System**: Learning from user interactions and preferences

#### 🔌 **LLM Integration** (`core/llm_client.py`)
- **Gemini API**: Real-time AI responses with robust error handling
- **Mock Mode**: Intelligent fallback for development and offline use
- **Response Parsing**: Multi-strategy parsing for reliable tool execution
- **Parameter Mapping**: Automatic parameter normalization across LLM variations

#### 🎨 **CLI Interface** (`interface/cli.py`)
- **Rich Formatting**: Beautiful output with colors, panels, and progress indicators
- **Interactive Prompts**: Context-aware user interactions and confirmations
- **Help System**: Comprehensive command documentation and examples
- **Error Handling**: Graceful error display and recovery suggestions

#### 🛡️ **Safety System** (`safety/approval.py`)
- **Risk Assessment**: 5-level classification with context-aware rules
- **Approval Workflows**: Beautiful approval panels with detailed warnings
- **Operation Tracking**: Audit trail of all safety decisions
- **Smart Defaults**: Sensible risk levels for different operation types

## 🔧 Tool Reference

### File Operations (4 tools)
| Tool | Description | Risk Level | Example |
|------|-------------|------------|---------|
| `read_file` | Read and display file contents | SAFE | `show me main.py` |
| `write_file` | Create or modify files | SAFE/LOW | `create calculator.py` |
| `list_files` | List directory contents | SAFE | `list files` |
| `create_folder` | Create new directories | SAFE | `create folder tests` |

### Destructive Operations (2 tools)
| Tool | Description | Risk Level | Example |
|------|-------------|------------|---------|
| `delete_file` | Delete files | LOW/HIGH | `delete old_file.py` |
| `delete_folder` | Delete directories | MEDIUM/HIGH | `delete folder temp` |

### Code Execution (3 tools)
| Tool | Description | Risk Level | Example |
|------|-------------|------------|---------|
| `run_python` | Execute Python files | LOW | `run calculator.py` |
| `run_command` | Execute shell commands | MEDIUM/HIGH | `run command "ls -la"` |
| `check_syntax` | Validate Python syntax | SAFE | `check syntax main.py` |

### Git Operations (8 tools)
| Tool | Description | Risk Level | Example |
|------|-------------|------------|---------|
| `git_status` | Repository status | SAFE | `git status` |
| `git_diff` | Show changes | SAFE | `git diff main.py` |
| `git_add` | Stage files | LOW | `git add main.py` |
| `git_commit` | Commit changes | LOW/MEDIUM | `git commit "Fix bug"` |
| `git_push` | Push to remote | MEDIUM/HIGH | `git push origin main` |
| `git_pull` | Pull from remote | LOW | `git pull origin main` |
| `git_log` | Show commit history | SAFE | `git log 10` |
| `git_branch` | Manage branches | LOW/HIGH | `git branch create feature` |

### Analysis Tools (5 tools)
| Tool | Description | Risk Level | Example |
|------|-------------|------------|---------|
| `python_lint` | Code style analysis | SAFE | `lint main.py` |
| `analyze_complexity` | Complexity metrics | SAFE | `analyze complexity main.py` |
| `security_scan` | Security vulnerabilities | SAFE | `security scan main.py` |
| `analyze_dependencies` | Dependency analysis | SAFE | `analyze dependencies` |
| `code_quality` | Comprehensive analysis | SAFE | `code quality main.py` |

### Code Writing Tools (4 tools)
| Tool | Description | Risk Level | Example |
|------|-------------|------------|---------|
| `generate_code` | AI-powered code generation | LOW/MEDIUM | `generate calculator code to calc.py` |
| `code_template` | Professional code templates | SAFE | `code template python_script` |
| `refactor_code` | Automated code improvement | MEDIUM | `refactor code main.py` |
| `code_snippet` | Common patterns & snippets | SAFE | `code snippet singleton` |

## 🔍 Analysis Features

### Python Linting
- **Syntax Validation**: AST-based syntax checking
- **Style Issues**: Line length, naming conventions, code structure
- **Best Practices**: Function complexity, exception handling
- **Maintenance**: TODO comments, debug statements

### Security Scanning
- **Injection Vulnerabilities**: SQL, command, and code injection detection
- **Hardcoded Secrets**: API keys, passwords, tokens
- **Dangerous Functions**: eval(), exec(), pickle.loads()
- **Insecure Practices**: Weak random, debug mode, HTTP URLs

### Complexity Analysis
- **Cyclomatic Complexity**: Decision point analysis
- **Function Metrics**: Length, arguments, complexity per function
- **Quality Scoring**: 0-100 automated assessment
- **Recommendations**: Specific improvement suggestions

### Example Analysis Output
```bash
🤖 CodeBuddy: security scan vulnerable_code.py

🔒 Security Scan Results for vulnerable_code.py:

🚨 High Severity:
  • Line 15: Command injection risk with string concatenation
    Code: `os.system("rm " + user_input)`
  • Line 23: eval() can execute arbitrary code
    Code: `result = eval(expression)`

⚠️ Medium Severity:
  • Line 8: Hardcoded secret detected
    Code: `API_KEY = "sk-1234567890abcdef"`

📊 Summary: 2 high, 1 medium, 0 low (3 total)

🔧 Immediate Actions Required:
  • Review and fix high-severity vulnerabilities immediately
  • Use subprocess with shell=False and validate inputs
  • Store secrets in environment variables or secure vaults
```

## ✨ Code Writing Features

### AI Code Generation
- **Natural Language to Code**: Convert descriptions into working Python programs
- **Specialized Generators**: Calculator, web scraper, API client, Flask app, CLI tool, database operations
- **File Output**: Direct code generation to specified files
- **Context Awareness**: Intelligent code structure based on requirements

### Professional Templates
- **10+ Template Types**: python_script, python_module, test_file, config_file, dockerfile, requirements, gitignore, readme, setup_py, makefile
- **Customizable Parameters**: Personalized templates with project-specific details
- **Best Practices**: Production-ready code following Python standards
- **Instant Scaffolding**: Complete project structure generation

### Smart Refactoring
- **6 Refactoring Types**: auto, extract_functions, improve_naming, add_docstrings, optimize_imports, add_type_hints
- **AST-Based Analysis**: Intelligent code parsing and transformation
- **Safety Backups**: Automatic backup creation before refactoring
- **Improvement Metrics**: Before/after statistics and quality scores

### Code Snippets
- **Design Patterns**: Singleton, Factory, Decorator, Context Manager
- **Common Functions**: File operations, JSON handling, error management, logging
- **Data Structures**: Linked list, binary tree, queue, stack implementations
- **Algorithms**: Binary search, quicksort, fibonacci, and more
- **Web/API Patterns**: Flask routes, FastAPI endpoints, requests wrappers

### Example Code Generation
```bash
🤖 CodeBuddy: generate calculator code to calculator.py

✅ Generated calculator.py (45 lines, 1.2KB)

📋 Generated Features:
  • Basic arithmetic operations (add, subtract, multiply, divide)
  • Input validation and error handling
  • Interactive command-line interface
  • Division by zero protection
  • Clean, documented code structure
```

## 🛡️ Safety System Details

### Risk Assessment Rules

#### File Operations
- **SAFE**: Reading files, listing directories
- **LOW**: Creating files, small file deletion
- **MEDIUM**: Large file operations, overwriting important files
- **HIGH**: Deleting critical files (main.py, .env, requirements.txt)

#### Git Operations
- **SAFE**: Status, diff, log (read-only operations)
- **LOW**: Adding files, committing to feature branches
- **MEDIUM**: Pushing to feature branches, pulling changes
- **HIGH**: Pushing to main/master/production branches

#### Command Execution
- **LOW**: Safe commands (ls, pwd, cat)
- **MEDIUM**: Installation commands (pip install, npm install)
- **HIGH**: File manipulation (rm, chmod, sudo)
- **CRITICAL**: Destructive commands (rm -rf, format, shutdown)

#### Code Writing Operations
- **SAFE**: Code templates, snippets (read-only generation)
- **LOW**: Simple code generation, basic refactoring
- **MEDIUM**: Complex code generation with file output, advanced refactoring
- **HIGH**: Refactoring critical files (main.py, __init__.py)

### Approval Interface
The safety system provides rich, contextual approval prompts:

```bash
⚠️  HIGH RISK OPERATION

Operation: Delete file: important_config.py
Details:
• filepath: important_config.py
• size: 2.5 KB
• type: Configuration file

Warnings:
• ⚠️  This operation affects important files/directories
• ⚠️  This action cannot be easily undone

Do you want to proceed with this high operation? (y/N):
```

## 🧪 Testing

The project includes comprehensive test suites in the `tests/` directory:

### Test Categories
- **Unit Tests**: Individual tool functionality
- **Integration Tests**: Tool coordination and workflows
- **Safety Tests**: Risk assessment and approval systems
- **LLM Tests**: Response parsing and parameter handling
- **CLI Tests**: User interface and interaction flows

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python tests/test_analysis_tools.py
python tests/test_git_tools.py
python tests/test_safety_system.py

# Debug mode tests
python tests/debug_real_llm.py
```

### Test Files
- `test_analysis_tools.py`: Code analysis functionality
- `test_git_tools.py`: Git operations and workflows
- `test_safety_system.py`: Safety approval system
- `test_new_features.py`: Feature integration tests
- `debug_*.py`: Development and debugging utilities

## 🔧 Development

### Adding New Tools
1. Create tool class in appropriate `tools/` module
2. Implement `execute()` method with proper error handling
3. Register tool in `main.py` with appropriate wrapper
4. Add safety rules in `safety/approval.py`
5. Update CLI help in `interface/cli.py`
6. Add LLM command handling in `core/llm_client.py`

### Example Tool Implementation
```python
class NewTool:
    """Description of what this tool does"""

    def execute(self, param1: str, param2: int = 10) -> str:
        """Execute the tool with given parameters"""
        try:
            # Tool implementation
            result = perform_operation(param1, param2)
            return f"✅ Operation successful: {result}"
        except Exception as e:
            return f"❌ Operation failed: {e}"
```

## 📊 Performance & Metrics

### Tool Execution Times
- **File Operations**: < 100ms average
- **Git Operations**: 200-500ms average
- **Analysis Tools**: 500ms-2s depending on file size
- **LLM Requests**: 1-3s with Gemini API

### Memory Usage
- **Base Agent**: ~50MB
- **With All Tools**: ~80MB
- **Analysis Cache**: ~20MB additional

### Supported File Types
- **Primary**: Python (.py)
- **Configuration**: JSON, YAML, TOML, INI
- **Documentation**: Markdown, text files
- **Dependencies**: requirements.txt, Pipfile, pyproject.toml

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`python -m pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation and help text
- Ensure safety system integration
- Test with both real and mock LLM modes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini API** for powerful LLM capabilities
- **Rich Library** for beautiful CLI formatting
- **Python AST** for code analysis capabilities
- **Git** for version control integration

---

**Built with ❤️ for developers who want an intelligent, safe, and powerful coding companion.**

*CodeBuddy - Where AI meets development productivity.*
