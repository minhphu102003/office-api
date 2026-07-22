import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.config import settings
from app.models.schemas import (
    CreateRequest,
    AddRequest,
    SetRequest,
    GetRequest,
    QueryRequest,
    RemoveRequest,
    MoveRequest,
    BatchRequest,
    ViewRequest,
    MergeRequest,
    GenerateRequest,
    ChatRequest,
    ApiResponse,
    BatchCommand,
)
from app.services.office_service import OfficeService, OfficeCliError
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/v1")
office = OfficeService()
llm = LLMService()


def _resolve_path(filename: str) -> str:
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir / filename)


def _handle_cli_error(e: OfficeCliError):
    raise HTTPException(
        status_code=400,
        detail=ApiResponse(
            success=False,
            error={
                "code": e.code,
                "message": e.message,
                "suggestion": e.suggestion,
            },
        ).model_dump(),
    )


@router.get("/health")
async def health():
    try:
        ver = office.version()
    except Exception:
        ver = "unknown"
    return {"success": True, "officecli_version": ver}


@router.post("/documents/create")
async def create_document(req: CreateRequest):
    filepath = _resolve_path(req.filename)
    if not filepath.endswith(f".{req.format}"):
        filepath = f"{filepath}.{req.format}"
    try:
        office.create(filepath)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True, path=os.path.abspath(filepath))


@router.post("/documents/{filename}/add")
async def add_to_document(filename: str, req: AddRequest):
    filepath = _resolve_path(filename)
    try:
        result = office.add(
            filepath,
            parent=req.parent,
            type_=req.type,
            props=req.props,
            after=req.after,
            before=req.before,
            index=req.index,
        )
    except OfficeCliError as e:
        _handle_cli_error(e)
    path = result.get("path", result.get("id", ""))
    return ApiResponse(success=True, path=path, data=result)


@router.post("/documents/{filename}/set")
async def set_document_property(filename: str, req: SetRequest):
    filepath = _resolve_path(filename)
    try:
        office.set(
            filepath,
            path=req.path,
            props=req.props,
            find=req.find,
            replace=req.replace,
        )
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True)


@router.post("/documents/{filename}/get")
async def get_document(filename: str, req: GetRequest):
    filepath = _resolve_path(filename)
    try:
        result = office.get(
            filepath,
            path=req.path,
            depth=req.depth,
        )
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True, data=result)


@router.post("/documents/{filename}/query")
async def query_document(filename: str, req: QueryRequest):
    filepath = _resolve_path(filename)
    try:
        result = office.query(filepath, req.selector)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True, data=result)


@router.post("/documents/{filename}/remove")
async def remove_from_document(filename: str, req: RemoveRequest):
    filepath = _resolve_path(filename)
    try:
        office.remove(filepath, req.path)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True)


@router.post("/documents/{filename}/move")
async def move_in_document(filename: str, req: MoveRequest):
    filepath = _resolve_path(filename)
    try:
        office.move(
            filepath,
            path=req.path,
            to=req.to,
            index=req.index,
            after=req.after,
            before=req.before,
        )
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True)


def _batch_command_to_dict(cmd: BatchCommand) -> dict:
    d = {"command": cmd.command}
    if cmd.parent is not None:
        d["parent"] = cmd.parent
    if cmd.type is not None:
        d["type"] = cmd.type
    if cmd.path is not None:
        d["path"] = cmd.path
    if cmd.props:
        d["props"] = cmd.props
    if cmd.to is not None:
        d["to"] = cmd.to
    if cmd.index is not None:
        d["index"] = cmd.index
    if cmd.selector is not None:
        d["selector"] = cmd.selector
    if cmd.depth is not None:
        d["depth"] = cmd.depth
    if cmd.find is not None:
        d["find"] = cmd.find
    if cmd.replace is not None:
        d["replace"] = cmd.replace
    if cmd.mode is not None:
        d["mode"] = cmd.mode
    return d


@router.post("/documents/{filename}/batch")
async def batch_document(filename: str, req: BatchRequest):
    filepath = _resolve_path(filename)
    commands = [_batch_command_to_dict(c) for c in req.commands]
    try:
        result = office.batch(filepath, commands, stop_on_error=req.stop_on_error)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True, results=result)


@router.get("/documents/{filename}/view")
async def view_document(
    filename: str,
    mode: str = Query("outline"),
):
    filepath = _resolve_path(filename)
    try:
        result = office.view(filepath, mode)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True, data=result)


@router.post("/documents/{filename}/validate")
async def validate_document(filename: str):
    filepath = _resolve_path(filename)
    try:
        result = office.validate(filepath)
    except OfficeCliError as e:
        _handle_cli_error(e)
    issues = result.get("issues", [])
    return ApiResponse(success=True, issues=issues)


@router.post("/documents/{filename}/merge")
async def merge_document(filename: str, req: MergeRequest):
    filepath = _resolve_path(filename)
    out_path = filepath.replace(".", "_merged.")
    data = req.data or {}
    try:
        result = office.merge(filepath, out_path, data)
    except OfficeCliError as e:
        _handle_cli_error(e)
    merged_path = result.get("path", out_path)
    return ApiResponse(success=True, path=merged_path)


@router.get("/documents/{filename}/download")
async def download_document(filename: str):
    filepath = _resolve_path(filename)
    path = Path(filepath)
    if not path.exists():
        for ext in [".docx", ".xlsx", ".pptx"]:
            p = path.with_suffix(ext)
            if p.exists():
                path = p
                break
        else:
            raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(path), filename=path.name)


@router.post("/documents/{filename}/open")
async def open_document(filename: str):
    filepath = _resolve_path(filename)
    try:
        office.open(filepath)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True, resident=True)


@router.post("/documents/{filename}/save")
async def save_document(filename: str):
    filepath = _resolve_path(filename)
    try:
        office.save(filepath)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True)


@router.post("/documents/{filename}/close")
async def close_document(filename: str):
    filepath = _resolve_path(filename)
    try:
        office.close(filepath)
    except OfficeCliError as e:
        _handle_cli_error(e)
    return ApiResponse(success=True)


@router.post("/generate")
async def generate_document(req: GenerateRequest):
    filepath = _resolve_path(req.filename)
    if not filepath.endswith(f".{req.format}"):
        filepath = f"{filepath}.{req.format}"

    commands = await llm.generate_commands(req.prompt, req.format)
    create_cmd = {"command": "create", "file": filepath}
    if not any(c.get("command") == "create" for c in commands):
        commands.insert(0, create_cmd)

    summary = f"Đã tạo file {req.filename} với {len(commands)} thao tác"

    try:
        for cmd in commands:
            c = cmd.get("command", "")
            if c == "create":
                office.create(cmd.get("file", filepath))
            elif c == "add":
                office.add(
                    cmd.get("file", filepath),
                    parent=cmd.get("parent", "/"),
                    type_=cmd.get("type", "shape"),
                    props=cmd.get("props", {}),
                )
            elif c == "set":
                office.set(
                    cmd.get("file", filepath),
                    path=cmd.get("path", "/"),
                    props=cmd.get("props", {}),
                )
            elif c == "remove":
                office.remove(cmd.get("file", filepath), cmd.get("path", ""))
            elif c == "move":
                office.move(
                    cmd.get("file", filepath),
                    path=cmd.get("path", ""),
                    to=cmd.get("to", "/"),
                    index=cmd.get("index"),
                )
    except OfficeCliError as e:
        _handle_cli_error(e)

    return ApiResponse(
        success=True,
        summary=summary,
        path=os.path.abspath(filepath),
    )


@router.post("/chat")
async def chat_with_document(req: ChatRequest):
    filepath = _resolve_path(req.filename)
    history_dicts = [m.model_dump() for m in req.history]

    reply, actions = await llm.chat_with_commands(req.message, req.filename, history_dicts)

    try:
        for action in actions:
            cmd = action.get("command", "")
            if cmd == "create":
                office.create(action.get("file", filepath))
            elif cmd == "add":
                office.add(
                    action.get("file", filepath),
                    parent=action.get("parent", "/"),
                    type_=action.get("type", "shape"),
                    props=action.get("props", {}),
                )
            elif cmd == "set":
                office.set(
                    action.get("file", filepath),
                    path=action.get("path", "/"),
                    props=action.get("props", {}),
                )
            elif cmd == "remove":
                office.remove(action.get("file", filepath), action.get("path", ""))
            elif cmd == "move":
                office.move(
                    action.get("file", filepath),
                    path=action.get("path", ""),
                    to=action.get("to", "/"),
                    index=action.get("index"),
                )
    except OfficeCliError as e:
        _handle_cli_error(e)

    return ApiResponse(success=True, reply=reply, actions=actions)
