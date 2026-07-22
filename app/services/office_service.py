import subprocess
import json
import os
from pathlib import Path
from typing import Any, Optional
from app.config import settings


class OfficeCliError(Exception):
    def __init__(self, code: str, message: str, suggestion: str = ""):
        self.code = code
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"[{code}] {message}")


class OfficeService:
    def __init__(self, binary_path: Optional[str] = None):
        self.binary = binary_path or settings.officecli_path

    def _run(self, *args, timeout: int = 30) -> dict:
        cmd = [self.binary]
        cmd.extend(str(a) for a in args)
        cmd.append("--json")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise OfficeCliError("timeout", f"Command timed out after {timeout}s")

        if result.returncode != 0:
            try:
                err = json.loads(result.stderr)
                raise OfficeCliError(
                    code=err.get("code", "unknown"),
                    message=err.get("message", result.stderr.strip()),
                    suggestion=err.get("suggestion", ""),
                )
            except (json.JSONDecodeError, TypeError):
                raise OfficeCliError(
                    code="cli_error",
                    message=result.stderr.strip() or result.stdout.strip(),
                )

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout.strip()}

    def version(self) -> str:
        cmd = [self.binary, "--version"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip() or result.stderr.strip() or "unknown"
            return "unknown"
        except Exception:
            return "unknown"

    def create(self, filepath: str) -> dict:
        return self._run("create", filepath)

    def add(
        self,
        filepath: str,
        parent: str,
        type_: str,
        props: Optional[dict[str, Any]] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        index: Optional[int] = None,
    ) -> dict:
        cmd = ["add", filepath, parent, "--type", type_]
        if props:
            for k, v in props.items():
                cmd.extend(["--prop", f"{k}={v}"])
        if after is not None:
            cmd.extend(["--after", after])
        if before is not None:
            cmd.extend(["--before", before])
        if index is not None:
            cmd.extend(["--index", str(index)])
        return self._run(*cmd)

    def set(
        self,
        filepath: str,
        path: str,
        props: Optional[dict[str, Any]] = None,
        find: Optional[str] = None,
        replace: Optional[str] = None,
    ) -> dict:
        cmd = ["set", filepath, path]
        if props:
            for k, v in props.items():
                cmd.extend(["--prop", f"{k}={v}"])
        if find is not None:
            cmd.extend(["--find", find])
        if replace is not None:
            cmd.extend(["--replace", replace])
        return self._run(*cmd)

    def get(self, filepath: str, path: str = "/", depth: int = 2) -> dict:
        cmd = ["get", filepath, path, "--depth", str(depth)]
        return self._run(*cmd)

    def query(self, filepath: str, selector: str) -> dict:
        return self._run("query", filepath, selector)

    def remove(self, filepath: str, path: str) -> dict:
        return self._run("remove", filepath, path)

    def move(
        self,
        filepath: str,
        path: str,
        to: str,
        index: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> dict:
        cmd = ["move", filepath, path, "--to", to]
        if index is not None:
            cmd.extend(["--index", str(index)])
        if after is not None:
            cmd.extend(["--after", after])
        if before is not None:
            cmd.extend(["--before", before])
        return self._run(*cmd)

    def batch(self, filepath: str, commands: list[dict], stop_on_error: bool = False) -> dict:
        cmds_json = json.dumps(commands)
        cmd = ["batch", filepath, cmds_json]
        if stop_on_error:
            cmd.append("--stop-on-error")
        return self._run(*cmd, timeout=120)

    def view(self, filepath: str, mode: str = "outline") -> dict:
        return self._run("view", filepath, mode)

    def validate(self, filepath: str) -> dict:
        return self._run("validate", filepath)

    def merge(self, filepath: str, output_path: str, data: dict) -> dict:
        data_json = json.dumps(data)
        return self._run("merge", filepath, output_path, data_json)

    def open(self, filepath: str) -> dict:
        return self._run("open", filepath)

    def save(self, filepath: str) -> dict:
        return self._run("save", filepath)

    def close(self, filepath: str) -> dict:
        return self._run("close", filepath)
