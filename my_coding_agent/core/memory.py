"""
Agent Memory - Context and learning system
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os


class AgentMemory:
    """Manages agent memory and learning"""
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        self.session_memory = []
        self.persistent_memory = self._load_persistent_memory()
    
    def add_interaction(self, user_input: str, result: str, context: Dict[str, Any]):
        """Store an interaction in memory"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "result": result,
            "success": not result.startswith("❌"),
            "context": context
        }
        
        # Add to session memory
        self.session_memory.append(interaction)
        
        # Keep session memory manageable
        if len(self.session_memory) > 50:
            self.session_memory = self.session_memory[-30:]
        
        # Store successful patterns in persistent memory
        if interaction["success"]:
            self._learn_from_success(interaction)
    
    def get_recent_actions(self, count: int = 5) -> List[str]:
        """Get recent actions for context"""
        recent = self.session_memory[-count:] if self.session_memory else []
        return [f"{item['user_input']} → {item['result'][:50]}..." for item in recent]
    
    def get_context_for_request(self, user_input: str) -> Dict[str, Any]:
        """Get relevant context for a request"""
        context = {
            "similar_requests": self._find_similar_requests(user_input),
            "recent_files": self._get_recent_files(),
            "session_summary": self._get_session_summary()
        }
        return context
    
    def _load_persistent_memory(self) -> Dict[str, Any]:
        """Load persistent memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "successful_patterns": [],
            "user_preferences": {},
            "learned_shortcuts": {}
        }
    
    def _save_persistent_memory(self):
        """Save persistent memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.persistent_memory, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save memory: {e}")
    
    def _learn_from_success(self, interaction: Dict[str, Any]):
        """Learn patterns from successful interactions"""
        pattern = {
            "input_pattern": interaction["user_input"].lower(),
            "tool_used": self._extract_tool_from_result(interaction["result"]),
            "timestamp": interaction["timestamp"]
        }
        
        # Add to successful patterns
        self.persistent_memory["successful_patterns"].append(pattern)
        
        # Keep only recent patterns
        if len(self.persistent_memory["successful_patterns"]) > 100:
            self.persistent_memory["successful_patterns"] = \
                self.persistent_memory["successful_patterns"][-50:]
        
        # Save periodically
        if len(self.session_memory) % 10 == 0:
            self._save_persistent_memory()
    
    def _extract_tool_from_result(self, result: str) -> Optional[str]:
        """Extract tool name from result"""
        # Simple heuristic - look for tool patterns in result
        if "read_file" in result:
            return "read_file"
        elif "write_file" in result:
            return "write_file"
        elif "git_" in result:
            return "git_operation"
        elif "execute" in result:
            return "execute_code"
        return None
    
    def _find_similar_requests(self, user_input: str) -> List[Dict[str, Any]]:
        """Find similar past requests"""
        user_lower = user_input.lower()
        similar = []
        
        for pattern in self.persistent_memory["successful_patterns"]:
            if self._calculate_similarity(user_lower, pattern["input_pattern"]) > 0.6:
                similar.append(pattern)
        
        return similar[-3:]  # Return up to 3 most recent similar requests
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _get_recent_files(self) -> List[str]:
        """Get recently accessed files"""
        files = []
        for interaction in self.session_memory[-10:]:
            result = interaction.get("result", "")
            # Extract filenames from results
            import re
            file_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_./]*\.[a-zA-Z]+)', result)
            files.extend(file_matches)
        
        # Return unique files, most recent first
        return list(dict.fromkeys(reversed(files)))[:5]
    
    def _get_session_summary(self) -> str:
        """Get summary of current session"""
        if not self.session_memory:
            return "New session"
        
        total = len(self.session_memory)
        successful = sum(1 for item in self.session_memory if item["success"])
        
        return f"{successful}/{total} successful actions this session"
    
    def clear_session_memory(self):
        """Clear session memory"""
        self.session_memory = []
        self.context = {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "session_interactions": len(self.session_memory),
            "persistent_patterns": len(self.persistent_memory["successful_patterns"]),
            "recent_files": self._get_recent_files(),
            "session_summary": self._get_session_summary()
        }
