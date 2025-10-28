# 🧠 AI Agent – Powered by OpenRouter API

This project is a lightweight **local AI agent** that connects to the [OpenRouter API](https://openrouter.ai/) to run language models such as **Phi-3**, **Llama 3**, or **Mistral**.
It’s built for flexibility and simplicity — easy to extend, customize, and eventually support **offline execution** via local inference engines.

---

## 🚀 Features

* 🔗 Connects seamlessly to the **OpenRouter API**
* 💬 Interactive command-line or programmatic agent
* 🧩 Modular code structure for easy extension
* ⚙️ Environment-based configuration (`.env` support)
* 🛠️ Ready for future **offline/local mode** (Ollama, LM Studio, etc.)

---

## 🧰 Requirements

* Python **3.10+**
* `requests` or `openai` library
* An [OpenRouter](https://openrouter.ai/) API key

---

## ⚙️ Setup

1. **Clone the repo:**

   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1   # Windows
   # or
   source .venv/bin/activate    # Linux/macOS
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** and add your API key:

   ```
   OPENAI_API_KEY=your_openrouter_api_key
   BASE_URL=https://openrouter.ai/api/v1
   ```

---

## 🧠 Usage

Run the agent from your terminal:

```bash
python main.py
```

Or integrate it into your own scripts:

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="your_key")

response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct",
    messages=[{"role": "user", "content": "Summarize the history of AI in one paragraph"}]
)
print(response.choices[0].message.content)
```

---

## 🧩 Future Roadmap

* ✅ Cloud inference via OpenRouter
* 🔜 Offline mode using **Ollama** or **LM Studio**
* 🔜 Configurable model selection and personality profiles
* 🔜 Simple web UI for chat interactions
* 🔜 API endpoint for external integrations

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributing

Pull requests and suggestions are welcome!
If you’d like to help with the offline mode integration or new model support, feel free to open an issue or submit a PR.
