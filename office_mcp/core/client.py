import json
import subprocess
import os
from app.config import settings


def get_binary() -> str:
    return os.getenv("OFFICECLI_PATH", settings.officecli_path)


def run_officecli(*args: str, timeout: int = 30) -> dict:
    binary = get_binary()
    cmd = [binary, *args, "--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    if result.returncode != 0:
        try:
            return json.loads(result.stderr)
        except json.JSONDecodeError:
            return {"success": False, "error": result.stderr.strip() or result.stdout.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": True, "raw": result.stdout.strip()}
