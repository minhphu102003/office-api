import json
from typing import Optional
import httpx
from app.config import settings

SYSTEM_PROMPT = """Bạn là OfficeCLI assistant. Bạn có thể tạo và chỉnh sửa file Office (.docx, .xlsx, .pptx) thông qua OfficeCLI CLI.

Các lệnh bạn có thể dùng:
- officecli create <file>
- officecli add <file> <parent> --type <type> --prop key=value
- officecli set <file> <path> --prop key=value
- officecli get <file> <path> --json --depth N
- officecli query <file> <selector> --json
- officecli remove <file> <path>
- officecli move <file> <path> --to <parent> --index N
- officecli batch <file> <commands.json>
- officecli view <file> <mode>
- officecli validate <file>
- officecli merge <file> <out> <json_data>

Cheat sheet:
- Paths: /slide[1], /body/p[1], /Sheet1/A1, /slide[@id=123]
- Types: slide, shape, paragraph, run, cell, table, chart, picture, sheet, pivot
- Colors: FF0000, red, accent1, rgb(255,0,0)
- Dimensions: 2cm, 1in, 72pt, 96px
- Props format: --prop key=value (với Python SDK: "props": {"key": "value"})

Luôn trả về commands dưới dạng JSON array, mỗi command có:
{"command": "add", "file": "...", "parent": "...", "type": "...", "props": {...}}
"""


class LLMService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = settings.llm_model

    async def chat(self, messages: list[dict], system_prompt: Optional[str] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": 0.1,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_commands(self, prompt: str, format: str) -> list[dict]:
        user_prompt = (
            f"Hãy tạo một file .{format} dựa trên yêu cầu sau:\n\n{prompt}\n\n"
            f"Trả về JSON array các lệnh OfficeCLI cần thực thi."
        )
        content = await self.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=SYSTEM_PROMPT,
        )
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            lines = [l for l in lines if not l.startswith("```")]
            cleaned = "\n".join(lines)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return [{"command": "raw", "content": content}]

    async def chat_with_commands(
        self, message: str, filename: str, history: Optional[list[dict]] = None
    ) -> tuple[str, list[dict]]:
        history = history or []
        user_prompt = (
            f"File hiện tại: {filename}\n\n"
            f"Yêu cầu: {message}\n\n"
            f"Trả về JSON gồm:\n"
            f'  - "reply": nội dung trả lời (text)\n'
            f'  - "actions": mảng các lệnh OfficeCLI cần thực thi (nếu có)'
        )
        content = await self.chat(
            messages=history + [{"role": "user", "content": user_prompt}],
            system_prompt=SYSTEM_PROMPT,
        )
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            lines = [l for l in lines if not l.startswith("```")]
            cleaned = "\n".join(lines)
        try:
            result = json.loads(cleaned)
            reply = result.get("reply", content)
            actions = result.get("actions", [])
            return reply, actions
        except json.JSONDecodeError:
            return content, []
