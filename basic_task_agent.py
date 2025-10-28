# basic_agent_cloud.py
import requests
import os

def ask_agent(prompt, api_key):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free",  # Free model
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"❌ Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    print("🤖 Welcome to your Cloud AI Agent!")
    print("🔑 Get your free API key at: https://openrouter.ai/keys\n")
    
    api_key = input("Enter your OpenRouter API key: ").strip()
    
    if not api_key:
        print("❌ API key required!")
        return
    
    print("\n✅ Connected!")
    print("💡 Type 'exit' or 'quit' to stop\n")
    
    while True:
        user_input = input("\n🧩 > ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        print("\n⏳ Thinking...")
        answer = ask_agent(user_input, api_key)
        print(f"\n💡 {answer}")

if __name__ == "__main__":
    main()