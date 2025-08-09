import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class ConversationTurn:
    timestamp: str
    user_input: str
    agent_reasoning: str
    actions_taken: List[str]
    results: List[str]
    files_involved: List[str]
    success: bool
    lessons_learned: str = ""

@dataclass
class ProjectContext:
    project_path: str
    files_known: Dict[str, str]  # filepath -> last_known_content_hash
    patterns_learned: Dict[str, Any]
    user_preferences: Dict[str, Any]
    common_workflows: List[str]

class EnhancedMemory:
    def __init__(self, db_path: str = "codebuddy_memory.db"):
        self.db_path = db_path
        self.current_context = ProjectContext("", {}, {}, {}, [])
        self.conversation_history: List[ConversationTurn] = []
        self.working_memory: Dict[str, Any] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                agent_reasoning TEXT,
                actions_taken TEXT,
                results TEXT,
                files_involved TEXT,
                success BOOLEAN,
                lessons_learned TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_context (
                project_path TEXT PRIMARY KEY,
                files_known TEXT,
                patterns_learned TEXT,
                user_preferences TEXT,
                common_workflows TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_conversation_turn(self, turn: ConversationTurn):
        """Add a conversation turn to memory"""
        self.conversation_history.append(turn)
        
        # Persist to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, user_input, agent_reasoning, actions_taken, results, files_involved, success, lessons_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            turn.timestamp,
            turn.user_input,
            turn.agent_reasoning,
            json.dumps(turn.actions_taken),
            json.dumps(turn.results),
            json.dumps(turn.files_involved),
            turn.success,
            turn.lessons_learned
        ))
        
        conn.commit()
        conn.close()
    
    def get_conversation_context(self, last_n: int = 5) -> str:
        """Get recent conversation context for LLM"""
        recent_turns = self.conversation_history[-last_n:]
        
        context = "=== Recent Conversation Context ===\n"
        for turn in recent_turns:
            context += f"\nUser: {turn.user_input}\n"
            context += f"Agent Reasoning: {turn.agent_reasoning}\n"
            context += f"Actions: {', '.join(turn.actions_taken)}\n"
            context += f"Success: {turn.success}\n"
            if turn.lessons_learned:
                context += f"Lesson: {turn.lessons_learned}\n"
        
        return context
    
    def get_project_patterns(self) -> str:
        """Get learned patterns for current project"""
        patterns = self.current_context.patterns_learned
        if not patterns:
            return "No patterns learned yet for this project."
        
        pattern_text = "=== Learned Project Patterns ===\n"
        for pattern_type, pattern_data in patterns.items():
            pattern_text += f"{pattern_type}: {pattern_data}\n"
        
        return pattern_text
    
    def update_working_memory(self, key: str, value: Any):
        """Update working memory for current session"""
        self.working_memory[key] = value
    
    def get_working_memory(self) -> Dict[str, Any]:
        """Get current working memory state"""
        return self.working_memory.copy()
    
    def learn_pattern(self, pattern_type: str, pattern_data: Any):
        """Learn a new pattern"""
        self.current_context.patterns_learned[pattern_type] = pattern_data
        self._save_project_context()
    
    def _save_project_context(self):
        """Save project context to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO project_context 
            (project_path, files_known, patterns_learned, user_preferences, common_workflows)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            self.current_context.project_path,
            json.dumps(self.current_context.files_known),
            json.dumps(self.current_context.patterns_learned),
            json.dumps(self.current_context.user_preferences),
            json.dumps(self.current_context.common_workflows)
        ))
        
        conn.commit()
        conn.close()