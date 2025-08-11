"""
Core Agent - The brain of the coding assistant
Implements the Perceive → Reason → Act → Learn cycle
"""
import os
import re
from typing import Dict, List, Optional, Any
from .llm_client import LLMClient
from .memory import AgentMemory


class CodingAgent:
    """Main agent orchestrator implementing the core loop"""
    
    def __init__(self, llm_client: LLMClient, debug: bool = False, cli_interface=None):
        self.llm = llm_client
        self.debug = debug
        self.memory = AgentMemory()
        self.tools = {}  # Will be populated by tool registry
        self.context = {}  # Current session context
        self.cli = cli_interface
        self.safety_system = None  # Will be initialized when needed

        print(f"🤖 CodeBuddy initialized (LLM: {'Gemini' if llm_client.is_available() else 'Mock'})")
    
    def register_tool(self, name: str, tool_func):
        """Register a tool with the agent"""
        self.tools[name] = tool_func
        if self.debug:
            print(f"🔧 Registered tool: {name}")

    def _get_safety_system(self):
        """Get or create safety system"""
        if self.safety_system is None:
            from safety.approval import SafetyApprovalSystem
            self.safety_system = SafetyApprovalSystem(cli_interface=self.cli)
        return self.safety_system
    
    def process_request(self, user_input: str) -> str:
        """Main entry point - implements the core agent loop"""
        try:
            # PERCEIVE: Gather current state and context
            context = self._perceive(user_input)
            
            # REASON: Use LLM to plan actions
            plan = self._reason(user_input, context)
            
            # ACT: Execute the planned actions
            result = self._act(plan, user_input)
            
            # LEARN: Update memory and context
            self._learn(user_input, result, context)
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Agent error: {e}"
            if self.debug:
                import traceback
                error_msg += f"\n{traceback.format_exc()}"
            return error_msg
    
    def _perceive(self, user_input: str) -> Dict[str, Any]:
        """PERCEIVE: Gather current state and context"""
        context = {
            "user_input": user_input,
            "available_tools": list(self.tools.keys()),
            "working_directory": os.getcwd() if 'os' in globals() else ".",
            "recent_actions": self.memory.get_recent_actions(5),
            "session_context": self.context
        }
        
        if self.debug:
            print(f"🔍 PERCEIVE: {len(context['available_tools'])} tools available")
        
        return context
    
    def _reason(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """REASON: Use LLM to analyze and plan"""
        
        # Create reasoning prompt
        prompt = self._build_reasoning_prompt(user_input, context)
        
        # Get LLM response
        llm_response = self.llm.generate(prompt)
        
        # Parse response into actionable plan
        plan = self._parse_llm_response(llm_response, user_input)
        
        if self.debug:
            print(f"🧠 REASON: Plan type = {plan.get('type', 'unknown')}")
        
        return plan
    
    def _act(self, plan: Dict[str, Any], user_input: str) -> str:
        """ACT: Execute the planned actions"""
        
        plan_type = plan.get("type", "unknown")
        
        if plan_type == "tool_execution":
            return self._execute_tool_plan(plan)
        elif plan_type == "conversation":
            return plan.get("response", "I'm here to help with your coding tasks!")
        elif plan_type == "error":
            return plan.get("message", "I couldn't understand that request.")
        else:
            return "🤔 I'm not sure how to handle that request yet."
    
    def _learn(self, user_input: str, result: str, context: Dict[str, Any]):
        """LEARN: Update memory and context for future decisions"""
        
        # Store interaction in memory
        self.memory.add_interaction(user_input, result, context)
        
        # Update session context
        self.context["last_action"] = {
            "input": user_input,
            "result": result,
            "success": not result.startswith("❌")
        }
        
        if self.debug:
            print(f"📚 LEARN: Stored interaction (success: {not result.startswith('❌')})")
    
    def _build_reasoning_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build prompt for LLM reasoning"""
        
        tools_list = ", ".join(context["available_tools"])
        recent_actions = "\n".join([f"- {action}" for action in context["recent_actions"]])
        
        prompt = f"""You are an intelligent coding assistant. Analyze the user's request and respond with the appropriate action.

USER REQUEST: "{user_input}"

AVAILABLE TOOLS: {tools_list}

RECENT ACTIONS:
{recent_actions}

INSTRUCTIONS:
1. If the user wants to perform a coding task, respond with a tool command in this format: tool_name(param1="value1", param2="value2")
2. If the user is asking a question or being conversational, respond naturally
3. If you're unsure, ask for clarification

EXAMPLES:
- "show me main.py" → read_file(filepath="main.py")
- "create hello.py" → write_file(filepath="hello.py", content='''print("Hello, World!")''')
- "list files" → list_files(directory=".")
- "hello" → Natural conversational response

IMPORTANT: For write_file, always include both filepath and content parameters with triple quotes for multi-line content.

Respond with either a tool command or natural conversation:"""

        return prompt
    
    def _parse_llm_response(self, response: str, user_input: str) -> Dict[str, Any]:
        """Parse LLM response into actionable plan with robust parsing"""

        response = response.strip()



        # Try multiple parsing strategies

        # Strategy 1: Direct tool command pattern (most common)
        tool_match = re.search(r'(\w+)\((.*)\)$', response.strip(), re.DOTALL)

        if tool_match:
            tool_name = tool_match.group(1)
            params_str = tool_match.group(2)



            params = self._parse_tool_params(params_str)

            return {
                "type": "tool_execution",
                "tool": tool_name,
                "params": params,
                "raw_response": response
            }

        # Strategy 2: Look for tool commands anywhere in the response
        tool_pattern = r'(\w+)\(([^)]*(?:\([^)]*\)[^)]*)*)\)'
        all_matches = re.findall(tool_pattern, response, re.DOTALL)

        if all_matches:
            # Use the first valid tool match
            for tool_name, params_str in all_matches:
                if tool_name in self.tools:
                    if self.debug:
                        print(f"🔍 STRATEGY_2_SUCCESS: tool={tool_name}, params_str='{params_str}'")

                    params = self._parse_tool_params(params_str)

                    return {
                        "type": "tool_execution",
                        "tool": tool_name,
                        "params": params,
                        "raw_response": response
                    }

        # Strategy 3: Intelligent inference from natural language
        inferred_plan = self._infer_tool_from_natural_language(response, user_input)
        if inferred_plan:
            if self.debug:
                print(f"🔍 STRATEGY_3_SUCCESS: {inferred_plan}")
            return inferred_plan

        # Strategy 4: Fallback to conversational response
        if self.debug:
            print(f"🔍 FALLBACK_TO_CONVERSATION")

        return {
            "type": "conversation",
            "response": response
        }
    
    def _parse_tool_params(self, params_str: str) -> Dict[str, str]:
        """Parse tool parameters from string with robust parsing"""
        params = {}

        if not params_str.strip():
            return params



        # Strategy 1: Handle triple-quoted strings for multi-line content
        triple_quote_pattern = r'(\w+)="""(.*?)"""'
        triple_matches = re.findall(triple_quote_pattern, params_str, re.DOTALL)

        for key, value in triple_matches:
            params[key] = value.strip()
            # Remove this match from params_str to avoid double processing
            params_str = re.sub(rf'{key}=""".*?"""', '', params_str, flags=re.DOTALL)

        # Strategy 2: Handle regular quoted parameters (single and double quotes)
        param_pattern = r'(\w+)=(["\'])(.*?)\2'
        matches = re.findall(param_pattern, params_str)

        for match in matches:
            key, _, value = match
            params[key] = value
            # Remove processed parameter
            params_str = re.sub(rf'{key}=["\'][^"\']*["\']', '', params_str)

        # Strategy 3: Handle unquoted parameters
        unquoted_pattern = r'(\w+)=([^,\s)]+)'
        unquoted_matches = re.findall(unquoted_pattern, params_str)

        for key, value in unquoted_matches:
            if key not in params:  # Don't override already parsed params
                params[key] = value.strip()

        # Strategy 4: Handle positional parameters (fallback)
        if not params and params_str.strip():
            # If no named parameters found, try to infer from position
            parts = [p.strip() for p in params_str.split(',') if p.strip()]
            if parts:
                # First parameter is usually filepath/path
                first_param = parts[0].strip('\'"')
                if '.' in first_param or '/' in first_param or '\\' in first_param:
                    params['filepath'] = first_param
                else:
                    params['folderpath'] = first_param

                # Second parameter is usually content
                if len(parts) > 1:
                    params['content'] = parts[1].strip('\'"')

        # Strategy 5: Parameter name mapping (handle LLM variations)
        params = self._normalize_parameter_names(params)



        return params

    def _normalize_parameter_names(self, params: Dict[str, str]) -> Dict[str, str]:
        """Normalize parameter names to match tool expectations"""
        normalized = {}

        # Parameter name mappings
        name_mappings = {
            # Folder/directory parameters
            'folder_path': 'folderpath',
            'directory_path': 'folderpath',
            'dir_path': 'folderpath',
            'folder_name': 'folderpath',
            'directory_name': 'folderpath',
            'path': 'folderpath',  # Generic path for folders

            # File parameters
            'file_path': 'filepath',
            'filename': 'filepath',
            'file_name': 'filepath',

            # Command parameters
            'cmd': 'command',
            'shell_command': 'command',

            # Content parameters
            'file_content': 'content',
            'code': 'content',
            'text': 'content'
        }

        for key, value in params.items():
            # Use mapping if available, otherwise keep original
            normalized_key = name_mappings.get(key, key)
            normalized[normalized_key] = value

        return normalized

    def _infer_tool_from_natural_language(self, response: str, user_input: str) -> Optional[Dict[str, Any]]:
        """Infer tool commands from natural language responses"""
        import re
        response_lower = response.lower()
        user_lower = user_input.lower()

        # File creation inference
        if any(word in user_lower for word in ["create", "make", "write"]) and any(ext in user_lower for ext in [".py", ".txt", ".js", ".md"]):
            # Extract filename
            filename_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_./]*\.[a-zA-Z]+)', user_input)
            if filename_match:
                filename = filename_match.group(1)

                # Generate appropriate content
                if "hello" in user_lower:
                    content = 'print("Hello, World!")'
                elif "calculator" in user_lower:
                    content = '''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

print("Simple calculator functions created")'''
                else:
                    content = f'# {filename} - Created by CodingAgent\nprint("File created successfully!")'

                return {
                    "type": "tool_execution",
                    "tool": "write_file",
                    "params": {"filepath": filename, "content": content},
                    "raw_response": response
                }

        # Folder creation inference
        if "create" in user_lower and ("folder" in user_lower or "directory" in user_lower):
            words = user_input.split()
            folder_name = "new_folder"
            for i, word in enumerate(words):
                if word.lower() in ["folder", "directory"] and i + 1 < len(words):
                    folder_name = words[i + 1]
                    break

            return {
                "type": "tool_execution",
                "tool": "create_folder",
                "params": {"folderpath": folder_name},
                "raw_response": response
            }

        # File reading inference
        if any(word in user_lower for word in ["show", "read", "display"]) and any(ext in user_lower for ext in [".py", ".txt", ".js", ".md"]):
            filename_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_./]*\.[a-zA-Z]+)', user_input)
            if filename_match:
                filename = filename_match.group(1)
                return {
                    "type": "tool_execution",
                    "tool": "read_file",
                    "params": {"filepath": filename},
                    "raw_response": response
                }

        # Python execution inference
        if "run" in user_lower and ".py" in user_lower:
            filename_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_./]*\.py)', user_input)
            if filename_match:
                filename = filename_match.group(1)
                return {
                    "type": "tool_execution",
                    "tool": "run_python",
                    "params": {"filepath": filename},
                    "raw_response": response
                }

        # List files inference
        if "list" in user_lower and ("file" in user_lower or "directory" in user_lower):
            return {
                "type": "tool_execution",
                "tool": "list_files",
                "params": {"directory": "."},
                "raw_response": response
            }

        return None

    def _execute_tool_plan(self, plan: Dict[str, Any]) -> str:
        """Execute a tool-based plan with safety approval"""
        tool_name = plan["tool"]
        params = plan["params"]

        if tool_name not in self.tools:
            return f"❌ Unknown tool: {tool_name}"

        try:
            # Check if operation requires approval
            safety_system = self._get_safety_system()
            if safety_system.requires_approval(tool_name, **params):
                if self.debug:
                    print(f"�️  Requesting approval for: {tool_name}")

                approved = safety_system.request_approval(tool_name, **params)
                if not approved:
                    return f"❌ Operation cancelled by user: {tool_name}"

            if self.debug:
                print(f"🔧 Executing: {tool_name}({params})")

            tool_func = self.tools[tool_name]
            result = tool_func(**params)

            return result

        except Exception as e:
            return f"❌ Tool execution failed: {e}"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    def toggle_debug(self) -> str:
        """Toggle debug mode"""
        self.debug = not self.debug
        return f"🐛 Debug mode: {'ON' if self.debug else 'OFF'}"
