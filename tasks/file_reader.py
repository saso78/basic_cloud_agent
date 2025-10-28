# tools/file_tools.py
import os

def list_files():
    """List all files in the current directory."""
    return [f for f in os.listdir('.') if os.path.isfile(f)]

def read_file(filename):
    """Read a file safely."""
    if not os.path.exists(filename):
        return f"❌ File not found: {filename}"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Error reading file: {e}"
