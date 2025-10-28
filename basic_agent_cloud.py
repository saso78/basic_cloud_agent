# basic_agent_cloud.py
import os
import requests
from dotenv import load_dotenv
from tasks.file_reader import list_files, read_file

load_dotenv()

def ask_agent(prompt, api_key):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that provides short, clear answers."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    print("🤖 Task Agent + Tools Enabled (Cloud Mode)")
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ Missing API key! Set OPENROUTER_API_KEY in your .env file.")
        return

    print("✅ Agent ready. Type /help for commands.\n")

    while True:
        user_input = input("🧩 > ").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        # Handle tool commands first
        if user_input.startswith("/list"):
            print("\n📂 Files in current directory:\n")
            print("\n".join(list_files()))
            continue

        if user_input.startswith("/read "):
            filename = user_input.replace("/read ", "").strip()
            print(f"\n📖 Reading {filename}...\n")
            print(read_file(filename))
            continue

        if user_input.startswith("/help"):
            print("""
🛠️ Available commands:
  /list         → List all files in the current folder
  /read <file>  → Read and display a file's contents
  /help         → Show this help message
  exit          → Quit
""")
            continue

        # Otherwise, ask the AI model
        print("\n⏳ Thinking...")
        answer = ask_agent(user_input, api_key)
        print(f"\n💡 {answer}\n")

if __name__ == "__main__":
    main()
