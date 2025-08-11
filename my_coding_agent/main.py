#!/usr/bin/env python3
"""
My Coding Agent - Clean, intelligent AI coding assistant
Entry point for the application
"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.llm_client import GeminiClient
from core.agent import CodingAgent
from tools.base_tool import ToolRegistry
from tools.file_ops import create_file_tools
from tools.code_ops import create_code_tools
from tools.git_tools import (
    GitStatusTool, GitDiffTool, GitAddTool, GitCommitTool,
    GitPushTool, GitPullTool, GitLogTool, GitBranchTool
)
from tools.analysis_tools import PythonLinterTool, ComplexityAnalyzerTool, SecurityScannerTool
from tools.security_tools import DependencyAnalyzerTool, CodeQualityTool
from tools.code_writing_tools import CodeGeneratorTool
from tools.code_templates import CodeTemplateTool
from tools.code_refactoring import CodeRefactorTool
from tools.code_snippets import CodeSnippetTool
from interface.cli import CLI


def setup_environment():
    """Setup environment and configuration"""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  No GEMINI_API_KEY found in environment")
        print("💡 Create a .env file with your Gemini API key")
        print("🔄 Will use mock mode for development")
    
    return api_key


def create_git_tools():
    """Create Git operation tools"""
    from tools.base_tool import BaseTool

    # Create tool instances with proper names
    tools = []

    # Git status
    git_status = GitStatusTool()
    git_status.name = "git_status"
    tools.append(git_status)

    # Git diff
    git_diff = GitDiffTool()
    git_diff.name = "git_diff"
    tools.append(git_diff)

    # Git add
    git_add = GitAddTool()
    git_add.name = "git_add"
    tools.append(git_add)

    # Git commit
    git_commit = GitCommitTool()
    git_commit.name = "git_commit"
    tools.append(git_commit)

    # Git push
    git_push = GitPushTool()
    git_push.name = "git_push"
    tools.append(git_push)

    # Git pull
    git_pull = GitPullTool()
    git_pull.name = "git_pull"
    tools.append(git_pull)

    # Git log
    git_log = GitLogTool()
    git_log.name = "git_log"
    tools.append(git_log)

    # Git branch
    git_branch = GitBranchTool()
    git_branch.name = "git_branch"
    tools.append(git_branch)

    return tools


def create_analysis_tools():
    """Create code analysis tools"""
    tools = []

    # Python linter
    python_linter = PythonLinterTool()
    python_linter.name = "python_lint"
    tools.append(python_linter)

    # Complexity analyzer
    complexity_analyzer = ComplexityAnalyzerTool()
    complexity_analyzer.name = "analyze_complexity"
    tools.append(complexity_analyzer)

    # Security scanner
    security_scanner = SecurityScannerTool()
    security_scanner.name = "security_scan"
    tools.append(security_scanner)

    # Dependency analyzer
    dependency_analyzer = DependencyAnalyzerTool()
    dependency_analyzer.name = "analyze_dependencies"
    tools.append(dependency_analyzer)

    # Code quality tool
    code_quality = CodeQualityTool()
    code_quality.name = "code_quality"
    tools.append(code_quality)

    return tools


def create_code_writing_tools():
    """Create code writing and generation tools"""
    tools = []

    # Code generator
    code_generator = CodeGeneratorTool()
    code_generator.name = "generate_code"
    tools.append(code_generator)

    # Code templates
    code_template = CodeTemplateTool()
    code_template.name = "code_template"
    tools.append(code_template)

    # Code refactoring
    code_refactor = CodeRefactorTool()
    code_refactor.name = "refactor_code"
    tools.append(code_refactor)

    # Code snippets
    code_snippet = CodeSnippetTool()
    code_snippet.name = "code_snippet"
    tools.append(code_snippet)

    return tools


def create_agent(api_key: Optional[str] = None, debug: bool = False, cli_interface=None) -> CodingAgent:
    """Create and configure the coding agent"""

    # Initialize LLM client
    llm_client = GeminiClient(api_key=api_key)

    # Create agent with CLI interface for safety approvals
    agent = CodingAgent(llm_client, debug=debug, cli_interface=cli_interface)
    
    # Register tools
    tool_registry = ToolRegistry()
    
    # Add file operation tools
    for tool in create_file_tools():
        tool_registry.register(tool)
        # Register with agent using simple function wrapper
        def create_tool_wrapper(tool_instance):
            return lambda **kwargs: str(tool_instance.execute(**kwargs))
        agent.register_tool(tool.name, create_tool_wrapper(tool))

    # Add code execution tools
    for tool in create_code_tools():
        tool_registry.register(tool)
        # Register with agent using simple function wrapper
        def create_tool_wrapper(tool_instance):
            return lambda **kwargs: str(tool_instance.execute(**kwargs))
        agent.register_tool(tool.name, create_tool_wrapper(tool))

    # Add Git tools
    for tool in create_git_tools():
        tool_registry.register(tool)
        # Register with agent using simple function wrapper
        def create_tool_wrapper(tool_instance):
            return lambda **kwargs: str(tool_instance.execute(**kwargs))
        agent.register_tool(tool.name, create_tool_wrapper(tool))

    # Add Analysis tools
    for tool in create_analysis_tools():
        tool_registry.register(tool)
        # Register with agent using simple function wrapper
        def create_tool_wrapper(tool_instance):
            return lambda **kwargs: str(tool_instance.execute(**kwargs))
        agent.register_tool(tool.name, create_tool_wrapper(tool))

    # Add Code Writing tools
    for tool in create_code_writing_tools():
        tool_registry.register(tool)
        # Register with agent using simple function wrapper
        def create_tool_wrapper(tool_instance):
            return lambda **kwargs: str(tool_instance.execute(**kwargs))
        agent.register_tool(tool.name, create_tool_wrapper(tool))

    return agent


def main():
    """Main entry point"""
    print("🚀 Starting CodeBuddy...")
    
    # Setup
    api_key = setup_environment()
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Create CLI first
    cli = CLI("CodeBuddy")

    # Create agent with CLI interface for safety approvals
    agent = create_agent(api_key, debug=debug_mode, cli_interface=cli)

    # Start CLI
    cli.start(agent)


if __name__ == "__main__":
    main()
