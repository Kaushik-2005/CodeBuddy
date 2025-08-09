from typing import List, Dict, Optional
from datetime import datetime

class ConversationMemory:
    """Manages conversation context and history"""
    
    def __init__(self, max_interactions: int = 5, max_files: int = 10):
        self.max_interactions = max_interactions
        self.max_files = max_files
        self.conversation_history = []
        self.recent_files = []
        self.file_contexts = {}  # Store file-specific context
    
    def add_interaction(self, user_query: str, result: str, files_involved: List[str] = None):
        """Add a new interaction to memory"""
        interaction = {
            "timestamp": datetime.now(),
            "user_query": user_query,
            "result": result,
            "files_involved": files_involved or []
        }
        
        self.conversation_history.append(interaction)
        
        # Maintain size limit
        if len(self.conversation_history) > self.max_interactions:
            self.conversation_history.pop(0)
        
        # Update recent files
        if files_involved:
            for file in files_involved:
                if file in self.recent_files:
                    self.recent_files.remove(file)  # Remove to re-add at end
                self.recent_files.append(file)
        
        # Maintain file list size
        if len(self.recent_files) > self.max_files:
            self.recent_files.pop(0)
    
    def get_recent_files(self, count: int = 5) -> List[str]:
        """Get most recently worked on files"""
        return self.recent_files[-count:] if self.recent_files else []
    
    def get_last_file(self) -> Optional[str]:
        """Get the most recently worked on file"""
        return self.recent_files[-1] if self.recent_files else None
    
    def get_conversation_context(self, last_n: int = 3) -> str:
        """Get formatted conversation context"""
        if not self.conversation_history:
            return ""
        
        context = "Recent conversation:\n"
        recent_interactions = self.conversation_history[-last_n:]
        
        for i, interaction in enumerate(recent_interactions, 1):
            context += f"{i}. User: {interaction['user_query']}\n"
            if interaction['files_involved']:
                context += f"   Files: {', '.join(interaction['files_involved'])}\n"
        
        if self.recent_files:
            context += f"\nRecent files: {', '.join(self.get_recent_files())}\n"
        
        return context
    
    def find_file_by_reference(self, user_query: str) -> Optional[str]:
        """Try to resolve file references like 'it', 'the file', 'this'"""
        query_lower = user_query.lower()
        
        # Direct file references
        if any(ref in query_lower for ref in ['it', 'this', 'the file', 'that file']):
            return self.get_last_file()
        
        # Check if user mentions a specific file extension or pattern
        import re
        file_patterns = [
            r'([a-zA-Z0-9_./\\-]+\.(?:py|js|ts|java|cpp|c|md|txt|html|css))',
        ]
        
        for pattern in file_patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def is_modification_request(self, user_query: str) -> bool:
        """Check if user wants to modify recent work"""
        modification_indicators = [
            'modify', 'change', 'update', 'fix', 'correct', 'edit',
            'should', 'instead', 'not', 'rather than', 'improve',
            'add', 'remove', 'replace', 'better'
        ]
        return any(indicator in user_query.lower() for indicator in modification_indicators)
    
    def clear_memory(self):
        """Clear all memory (useful for starting fresh)"""
        self.conversation_history.clear()
        self.recent_files.clear()
        self.file_contexts.clear()
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about current memory state"""
        return {
            "total_interactions": len(self.conversation_history),
            "total_files": len(self.recent_files),
            "last_interaction": self.conversation_history[-1]["timestamp"] if self.conversation_history else None,
            "most_recent_file": self.get_last_file()
        }