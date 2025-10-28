def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"📘 File Content:\n{content[:500]}..."  # Preview first 500 chars
    except FileNotFoundError:
        return "❌ File not found."
