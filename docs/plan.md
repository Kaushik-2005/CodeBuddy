# Implementation Plan for AI Coding Agent

## Note on LLM Integration

Since OpenAI premium is not available and we do not want to run LLMs locally, we will use open-source LLMs that provide a public or self-hosted **API** (such as **Ollama API**, **Together.ai**, **Hugging Face Inference API**, or similar services).  
Additionally, we can use **langchain-gemini** for LLM integration, which provides a convenient interface for interacting with Gemini models via API.

## Phase 1: Foundation – Prove the Core Loop

**Goal:** Build a minimal viable agent that completes the Perceive → Reason → Act → Learn loop.

**Steps:**
1. **Project Setup**
   - Structure Python project
   - Manage dependencies (`requests`, `rich`, `sqlite3`, `gitpython`, `langchain-gemini`)
2. **LLM Integration Layer**
   - Abstract LLM provider class
   - Implement integration for open-source LLM APIs and Gemini via langchain-gemini (prompt, response parsing, error handling)
3. **Terminal Interface**
   - Basic CLI using Rich
   - Accept natural language input, display output
4. **Tool Execution Engine**
   - Implement `read_file` tool
   - Safely execute and return results
5. **Agent Loop**
   - Orchestrate Perceive (gather state), Reason (LLM), Act (tool), Learn (update memory)
6. **Test**
   - Ask “What’s in package.json?” and verify response

---

## Phase 2: Expand Tooling

**Goal:** Add more development tools for real workflows.

**Steps:**
1. **Filesystem Tools**
   - `write_file`, `search_codebase`, `get_structure`
2. **Git Tools**
   - `status`, `diff`, `commit`
3. **Code Analysis**
   - `run_linter`, `find_references`
4. **Execution**
   - `run_command`, `run_tests`
5. **Error Handling**
   - Tools return rich feedback and suggest fixes

---

## Phase 3: Safety & Recovery

**Goal:** Ensure safe, reversible operations.

**Steps:**
1. **Preview Mode**
   - Show diffs/previews before changes
2. **Approval Workflow**
   - Require user confirmation for destructive actions
3. **Rollback**
   - Use git for undo, maintain operation history
4. **Error Explanation**
   - Clear feedback and suggestions on failure

---

## Phase 4: Polish & Demonstrate

**Goal:** Refine UX, optimize, and document.

**Steps:**
1. **Streaming Responses**
   - Show progress for long operations
2. **Memory Optimization**
   - Smart context truncation, SQLite for persistent memory
3. **Learning**
   - Track user preferences, adapt autonomy
4. **Documentation**
   - Setup guide, architecture overview, usage examples
5. **Demo**
   - Record video, showcase real scenarios

---

## Architecture Principles

- **SOLID:** Each component has a single responsibility, is extensible, and uses abstractions.
- **Human-in-the-Loop:** User always controls destructive actions.
- **ReAct Loop:** Agent observes results and self-corrects.

---

## Next Steps

1. Scaffold the project and implement the minimal agent loop.
2. Incrementally add tools and safety features.
3. Continuously test with real codebases and refine