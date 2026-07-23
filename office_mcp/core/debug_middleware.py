import json
import sys


INSTRUCTIONS_SENT: bool = False


def _parse_sse_instructions(body: bytes) -> None:
    """Parse SSE response body and log InitializeResult instructions."""
    global INSTRUCTIONS_SENT
    for line in body.decode().split("\n"):
        line = line.strip()
        if not (line.startswith("data: ") or line.startswith("data:")):
            continue
        json_text = line[5:].strip()
        if not json_text:
            continue
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict) or "result" not in data:
            continue
        result = data["result"]
        inst = result.get("instructions")
        if inst is not None:
            INSTRUCTIONS_SENT = True
            print(
                f"[MCP-DEBUG] ✅ InitializeResult SENT with instructions"
                f" (len={len(inst)}, preview={inst[:80]!r})",
                file=sys.stderr,
            )
        elif "protocolVersion" in result:
            print(
                f"[MCP-DEBUG] ⚠️ InitializeResult WITHOUT instructions!"
                f" keys={list(result.keys())}",
                file=sys.stderr,
            )
        break


def _wrap_asgi_send(scope, receive, send):
    """Wrap the ASGI send call to detect InitializeResult in responses."""
    body_buffer: list[bytes] = []

    async def _logged_send(message):
        if message.get("type") != "http.response.body":
            await send(message)
            return
        body = message.get("body", b"")
        if body:
            body_buffer.append(body)
        if not message.get("more_body", False):
            full = b"".join(body_buffer)
            body_buffer.clear()
            _parse_sse_instructions(full)
        await send(message)

    return _logged_send


async def _debug_asgi_app(scope, receive, send, inner_app):
    if scope["type"] == "http":
        wrapped_send = _wrap_asgi_send(scope, receive, send)
        await inner_app(scope, receive, wrapped_send)
    else:
        await inner_app(scope, receive, send)


def wrap_asgi_app(inner_app):
    """Wrap an ASGI app with debug logging for InitializeResult."""

    async def _wrapped(scope, receive, send):
        await _debug_asgi_app(scope, receive, send, inner_app)

    return _wrapped
