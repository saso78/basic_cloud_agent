import requests
import os
import time
import subprocess
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "mistralai/mistral-7b-instruct",
    "meta-llama/llama-3-8b-instruct",
]

HISTORY_FILE = "chat_history.json"
MAX_HISTORY_MESSAGES = 10  # Keep last 5 exchanges (user + assistant = 10 messages)

class ConversationMemory:
    def __init__(self):
        self.messages = []
        self.session_start = datetime.now().isoformat()
        self.load_history()
    
    def load_history(self):
        """Load previous conversation from file."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load only recent messages
                    if 'messages' in data:
                        self.messages = data['messages'][-MAX_HISTORY_MESSAGES:]
                        print(f"📚 Loaded {len(self.messages)} messages from previous session")
            except Exception as e:
                print(f"⚠️ Could not load history: {e}")
    
    def save_history(self):
        """Save conversation to file."""
        try:
            data = {
                'session_start': self.session_start,
                'last_updated': datetime.now().isoformat(),
                'messages': self.messages
            }
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")
    
    def add_message(self, role, content):
        """Add a message to conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last N messages
        if len(self.messages) > MAX_HISTORY_MESSAGES:
            self.messages = self.messages[-MAX_HISTORY_MESSAGES:]
    
    def get_context_messages(self):
        """Get messages formatted for API (without timestamps)."""
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]
    
    def clear(self):
        """Clear current session memory."""
        self.messages = []
        print("🧹 Memory cleared!")
    
    def show_history(self):
        """Display conversation history."""
        if not self.messages:
            return "📭 No conversation history yet."
        
        output = "📜 Conversation History:\n" + "="*50 + "\n"
        for i, msg in enumerate(self.messages, 1):
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            output += f"\n{role_emoji} {msg['role'].upper()}: {msg['content'][:100]}...\n"
        return output

memory = ConversationMemory()

def ask_agent(prompt, api_key):
    """Ask AI with conversation context."""
    # Add system message + conversation history + new prompt
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Always reply in complete sentences."}
    ]
    messages.extend(memory.get_context_messages())
    messages.append({"role": "user", "content": prompt.strip()})
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for model in MODELS:
        print(f"🔁 Trying model: {model}")
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=45,
            )

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"].get("content", "").strip()
                    if content:
                        # Store in memory
                        memory.add_message("user", prompt.strip())
                        memory.add_message("assistant", content)
                        return f"(🧠 Model: {model})\n{content}"
                    else:
                        print(f"⚠️ Empty response from {model}, trying next...")
                        continue
                else:
                    print(f"⚠️ Unexpected format from {model}")
                    continue

            elif response.status_code == 429:
                print(f"⚠️ Rate limit for {model}, retrying next model...")
                time.sleep(2)
                continue
            else:
                print(f"❌ API Error {response.status_code}: {response.text[:200]}")
                continue

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout on model {model}, trying next...")
            continue
        except Exception as e:
            print(f"❌ Unexpected error on {model}: {e}")
            continue

    return "❌ All models are currently unavailable. Please try again later."

def run_local_command(command):
    """Safely execute small local commands."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip() or "✅ Command executed successfully (no output)"
    except Exception as e:
        return f"❌ Command error: {e}"

def read_file(path):
    """Read contents of a local file (text only)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()[:1000]
    except Exception as e:
        return f"❌ File read error: {e}"

def fetch_url(url):
    """Fetch data from a URL."""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text[:1000]
        else:
            return f"❌ HTTP {r.status_code} - {r.text[:200]}"
    except Exception as e:
        return f"❌ Fetch error: {e}"

def handle_command(user_input):
    """Detect and execute local commands."""
    if user_input.startswith("/read "):
        path = user_input.split(" ", 1)[1].strip()
        return read_file(path)
    elif user_input.startswith("/fetch "):
        url = user_input.split(" ", 1)[1].strip()
        return fetch_url(url)
    elif user_input.startswith("/run "):
        cmd = user_input.split(" ", 1)[1].strip()
        return run_local_command(cmd)
    elif user_input == "/history":
        return memory.show_history()
    elif user_input == "/clear":
        memory.clear()
        return "✅ Conversation memory cleared"
    elif user_input == "/help":
        return (
            "🧩 Commands available:\n"
            "/read <path>   – Read local file\n"
            "/fetch <url>   – Fetch content from the web\n"
            "/run <cmd>     – Run simple local command\n"
            "/history       – Show conversation history\n"
            "/clear         – Clear conversation memory\n"
            "/quit or exit  – Exit and save\n"
        )
    else:
        return None

def main():
    print("🤖 Task Agent + Memory + Tools (Cloud Mode)")
    print("✅ Commands: /help /history /clear /read /fetch /run\n")

    if not api_key:
        print("❌ Missing OPENROUTER_API_KEY in your .env file")
        return

    try:
        while True:
            user_input = input("\n🧩 > ").strip()
            if user_input.lower() in ["exit", "quit", "/quit"]:
                print("\n💾 Saving conversation...")
                memory.save_history()
                print("👋 Goodbye!")
                break
            if not user_input:
                continue

            # Local commands first
            local_response = handle_command(user_input)
            if local_response:
                print(f"\n💻 {local_response}\n")
                continue

            # Otherwise, ask the AI
            print("\n⏳ Thinking...\n")
            answer = ask_agent(user_input, api_key)
            print(f"\n💡 {answer}\n")
    
    except KeyboardInterrupt:
        print("\n\n💾 Saving conversation...")
        memory.save_history()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()