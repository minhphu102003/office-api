import re
from pathlib import Path
from typing import Any

SKILLS_DIR = Path(__file__).parent.parent / "skills"


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    body = match.group(2)
    meta: dict[str, Any] = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("|") and "\n" in body:
                continue
            meta[key] = val
    return meta, body


def load_skills() -> list[dict[str, Any]]:
    if not SKILLS_DIR.exists():
        return []
    skills = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.exists():
            continue
        text = skill_file.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        skills.append({
            "name": meta.get("name", entry.name),
            "description": meta.get("description", ""),
            "text": text,
            "path": skill_file,
        })
    return skills
