from pathlib import Path
import os

from config import settings

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"

print("\n=== ENV DEBUG ===")
print(f"Project Root : {PROJECT_ROOT}")
print(f"ENV File     : {ENV_FILE}")
print(f"ENV Exists   : {ENV_FILE.exists()}")

settings.load_env_file(ENV_FILE, override=True)

api_key = os.getenv("OPENAI_API_KEY", "")

print(f"Key Length   : {len(api_key)}")

if api_key:
    print(f"Key Start    : {api_key[:12]}")
    print(f"Key End      : {api_key[-8:]}")
else:
    print("OPENAI_API_KEY not found")

print("=================\n")
