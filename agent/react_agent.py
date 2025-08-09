from typing import Dict, List, Tuple, Optional
from memory.enhanced_memory import EnhancedMemory, ConversationTurn
from datetime import datetime
import json

class ReActAgent:
    def __init__(self, llm_provider, tool_registry, memory: EnhancedMemory, agent_instance=None):
        self.llm = llm_provider
        self.tools = tool_registry
        self.memory = memory
        self.agent = agent_instance  # Reference to main agent for tool execution
        self.max_iterations = 5
    
    def execute_task(self, user_input: str) -> str:
        """Execute a task using the ReAct loop: Reason → Act → Observe"""
        
        # Initialize conversation turn
        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            agent_reasoning="",
            actions_taken=[],
            results=[],
            files_involved=[],
            success=False
        )
        
        try:
            # PERCEIVE: Gather current state
            current_state = self._perceive()
            
            # Start ReAct loop
            for iteration in range(self.max_iterations):
                # REASON: Plan next action
                reasoning = self._reason(user_input, current_state, turn)
                turn.agent_reasoning += f"Iteration {iteration + 1}: {reasoning}\n"
                
                # Determine if task is complete
                if "TASK_COMPLETE" in reasoning:
                    turn.success = True
                    break
                
                # ACT: Execute planned action
                action, result = self._act(reasoning)
                turn.actions_taken.append(action)
                turn.results.append(result)
                
                # OBSERVE: Update state with results
                current_state = self._observe(current_state, action, result)
                
                # Check if we should continue
                if "ERROR" in result and iteration < self.max_iterations - 1:
                    continue
                elif "Successfully" in result:
                    turn.success = True
                    break
            
            # LEARN: Extract lessons and update memory
            lessons = self._learn(turn)
            turn.lessons_learned = lessons
            
            # Store conversation turn
            self.memory.add_conversation_turn(turn)
            
            return self._format_response(turn)
            
        except Exception as e:
            turn.success = False
            turn.lessons_learned = f"Error encountered: {e}"
            self.memory.add_conversation_turn(turn)
            return f"❌ Agent error: {e}"
    
    def _perceive(self) -> Dict[str, any]:
        """Gather current state information"""
        state = {
            "working_directory": ".",
            "recent_context": self.memory.get_conversation_context(),
            "project_patterns": self.memory.get_project_patterns(),
            "working_memory": self.memory.get_working_memory(),
            "available_tools": list(self.tools.get_all_tools().keys())
        }
        return state
    
    def _reason(self, user_input: str, current_state: Dict, turn: ConversationTurn) -> str:
        """Enhanced reasoning for ALL task types"""
        
        # Get recent context for better reasoning
        context = current_state.get('recent_context', '')
        available_tools = current_state.get('available_tools', [])
        
        reasoning_prompt = f"""
You are an intelligent coding agent. Analyze the situation and plan your next action.

USER REQUEST: {user_input}

AVAILABLE TOOLS: {', '.join(available_tools)}

RECENT CONTEXT:
{context}

PREVIOUS ACTIONS IN THIS TASK:
{turn.actions_taken}

PREVIOUS RESULTS:
{turn.results}

INSTRUCTIONS:
1. Analyze what the user wants to accomplish
2. Consider what you've already tried (if any)
3. Choose the most appropriate tool(s) for this task
4. If the task seems complete, respond with "TASK_COMPLETE: [explanation]"
5. Otherwise, specify exactly which tool to use and why

Common patterns:
- File operations: read_file, write_file, create_directory, get_structure
- Code analysis: validate_syntax, run_linter, analyze_complexity
- Execution: run_python, install_package, run_command
- Search: search_codebase, find_files, find_references

Respond with your reasoning and the specific tool command to execute.
Format: REASONING: [your analysis] ACTION: [tool_command]
"""
        
        return self.llm.ask(reasoning_prompt)
    
    def _act(self, reasoning: str) -> Tuple[str, str]:
        """Execute the planned action"""
        try:
            # Extract action from reasoning
            if "ACTION:" in reasoning:
                action_part = reasoning.split("ACTION:")[1].strip()
                action_line = action_part.split('\n')[0].strip()
                
                # Execute the tool command
                result = self._execute_tool_command(action_line)
                return action_line, result
            else:
                return "no_action", "No clear action found in reasoning"
                
        except Exception as e:
            return "error", f"Failed to execute action: {e}"
    
    def _observe(self, current_state: Dict, action: str, result: str) -> Dict:
        """Update state based on action results"""
        # Update working memory with results
        self.memory.update_working_memory("last_action", action)
        self.memory.update_working_memory("last_result", result)
        
        # Update state
        current_state["working_memory"] = self.memory.get_working_memory()
        
        return current_state
    
    def _learn(self, turn: ConversationTurn) -> str:
        """Extract lessons from the interaction"""
        
        learning_prompt = f"""
Analyze this interaction and extract key lessons:

USER INPUT: {turn.user_input}
ACTIONS TAKEN: {turn.actions_taken}
RESULTS: {turn.results}
SUCCESS: {turn.success}

What patterns, preferences, or insights can be learned from this interaction?
Keep it concise and actionable for future similar requests.
"""
        
        return self.llm.ask(learning_prompt)
    
    def _execute_tool_command(self, command: str) -> str:
        """Execute a tool command using the main agent's parsing logic"""
        try:
            if self.agent:
                # Use the main agent's tool execution method
                return self.agent.parse_and_execute_tool(command)
            else:
                # Fallback: direct tool execution
                return f"❌ Tool execution not available: {command}"
        except Exception as e:
            return f"❌ Tool execution failed: {e}"
    
    def _format_response(self, turn: ConversationTurn) -> str:
        """Format the final response to user"""
        if turn.success:
            return f"✅ Task completed successfully!\n\nActions taken: {', '.join(turn.actions_taken)}\n\nKey insight: {turn.lessons_learned}"
        else:
            return f"⚠️ Task encountered issues.\n\nAttempted: {', '.join(turn.actions_taken)}\n\nLessons: {turn.lessons_learned}"