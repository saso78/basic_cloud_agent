import requests
import os
import time
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

MODELS = [
    "mistralai/mistral-7b-instruct",
    "meta-llama/llama-3-8b-instruct",
    "nousresearch/hermes-2-pro-mistral-7b",
    "google/gemini-2.0-flash-exp:free"
]

def ask_agent(prompt, api_key):
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
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant. Always reply in complete sentences."},
                        {"role": "user", "content": prompt.strip()},
                    ],
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
                        return f"(🧠 Model: {model})\n{content}"
                    else:
                        print(f"⚠️ Empty response from {model}, trying next...")
                        continue
                else:
                    print(f"⚠️ Unexpected format from {model}: {data}")
                    continue

            elif response.status_code == 429:
                print(f"⚠️ Rate limit for {model}, retrying next model...")
                time.sleep(2)
                continue
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                continue

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout on model {model}, trying next...")
            continue
        except Exception as e:
            print(f"❌ Unexpected error on {model}: {e}")
            continue

    return "❌ All models are currently unavailable. Please try again later."

# ---------- COMMAND EXECUTION LAYER ----------

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
            return f.read()[:1000]  # limit to 1k chars for safety
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
    elif user_input == "/help":
        return (
            "🧩 Commands available:\n"
            "/read <path>   – Read local file\n"
            "/fetch <url>   – Fetch content from the web\n"
            "/run <cmd>     – Run simple local command\n"
            "/quit or exit  – Exit the agent\n"
        )
    else:
        return None

# ---------- MAIN LOOP ----------

def main():
    print("🤖 Task Agent + Tools Enabled (Cloud Mode)")
    print("✅ Commands: /help /read /fetch /run\n")

    if not api_key:
        print("❌ Missing OPENROUTER_API_KEY in your .env file")
        return

    while True:
        user_input = input("\n🧩 > ").strip()
        if user_input.lower() in ["exit", "quit"]:
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

if __name__ == "__main__":
    main()
