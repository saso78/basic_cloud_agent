# Basic Cloud AI Agent

🤖 **Basic Cloud AI Agent** is a Python-based, multi-model AI assistant that runs in your terminal. It uses OpenRouter's free API to interact with various LLMs and includes features such as command execution, persistent conversation memory, custom system prompts, and streaming output.

---

## Features

### 🌐 Multi-Model Cloud Support
- Supports multiple LLMs via OpenRouter API:
  - `google/gemini-2.0-flash-exp:free`
  - `mistralai/mistral-7b-instruct`
  - `meta-llama/llama-3-8b-instruct`
- Automatically rotates models if a model is rate-limited or unavailable.
- Streaming support for real-time output.

### 🧠 Subcontext Memory
- Stores the **last 5 user-assistant exchanges** in memory.
- **Persistent memory** saved to `chat_history.json` between sessions.
- Commands to view or clear memory:
  - `/history` – Show conversation history
  - `/clear` – Clear conversation memory

### 💻 Local Command Execution
- `/read <path>` – Read a local text file (limited to 1KB)
- `/fetch <url>` – Fetch content from a URL (limited to 1KB)
- `/run <command>` – Run a local shell command safely (sandboxed)
- These commands are executed locally before sending queries to the AI.

### 🎭 Customizable System Prompts
- Predefined system prompts for different assistant personalities:
  - `default`, `concise`, `expert`, `creative`, `teacher`, `coder`, `analyst`
- Switch prompts using:
  - `/prompts` – List available prompts
  - `/prompt <name>` – Switch to a preset prompt
  - `/custom <text>` – Set a custom system prompt

### ⚡ Streaming & CLI Interface
- Live token streaming for AI responses.
- Fully interactive terminal interface.
- Commands available:
```
/help – Show all available commands
/history – Show conversation history
/clear – Clear memory
/read – Read a local file
/fetch – Fetch URL content
/run – Run a shell command
/prompts – List system prompts
/prompt – Switch to a preset prompt
/custom – Set a custom system prompt
/quit – Exit the agent
```

### 💾 Persistent Memory
- Conversations are saved in `chat_history.json` automatically.
- On restart, the agent loads the last messages for context.

---

## Installation

## 1. Clone the repository:
```bash
git clone https://github.com/yourusername/basic_cloud_agent.git
cd basic_cloud_agent
```
## 2.Create a Python virtual environment:
```python -m venv .venv
```
## 3.Activate the environment:

  Windows:
   ```
   .venv\Scripts\activate
   ```
  macOS/Linux:
  ```
    source .venv/bin/activate
  ```  
## 4.Create a .env file with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```
### Usage
---
 Run the agent:
 ```
 python basic_agent_cloud.py
```
### Interact with the AI:  
```
🧩 > Hello
🧩 > /read notes.txt
🧩 > /fetch https://example.com
🧩 > /run dir
🧩 > /history
🧩 > /prompt expert
🧩 > /custom You are a funny assistant.
🧩 > /quit
```
---
### Future Enhancements
```
Offline support using local LLMs (Ollama, LLaMA, Mistral)
RAG (Retrieval-Augmented Generation) for querying PDFs, notes, or documents
Extended memory with summarization for long-term context
Web or GUI interface using Streamlit or Gradio
Plugin system for integrating APIs, tools, or databases
```
---
📜 License
This project is licensed under the MIT License — see the LICENSE file for details.
---
---
🙌 Contributing
Pull requests and suggestions are welcome! If you’d like to help with the offline mode integration or new model support, feel free to open an issue or submit a PR.
---
---
### Notes

This agent is currently optimized for free-tier OpenRouter API usage.
Be mindful when using /run — only run commands you trust.
Persistent memory grows over time; the history file can be trimmed or archived if needed.
---