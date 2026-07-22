from pydantic import BaseModel, Field
from typing import Any, Optional


class CreateRequest(BaseModel):
    filename: str
    format: str = Field(..., pattern=r"^(docx|xlsx|pptx)$")


class AddRequest(BaseModel):
    parent: str = "/"
    type: str
    props: dict[str, Any] = {}
    after: Optional[str] = None
    before: Optional[str] = None
    index: Optional[int] = None


class SetRequest(BaseModel):
    path: str
    props: dict[str, Any] = {}
    find: Optional[str] = None
    replace: Optional[str] = None


class GetRequest(BaseModel):
    path: str = "/"
    depth: int = 2
    json_mode: bool = True


class QueryRequest(BaseModel):
    selector: str


class RemoveRequest(BaseModel):
    path: str


class MoveRequest(BaseModel):
    path: str
    to: str
    index: Optional[int] = None
    after: Optional[str] = None
    before: Optional[str] = None


class BatchCommand(BaseModel):
    command: str
    parent: Optional[str] = None
    type: Optional[str] = None
    path: Optional[str] = None
    props: dict[str, Any] = {}
    to: Optional[str] = None
    index: Optional[int] = None
    selector: Optional[str] = None
    depth: Optional[int] = None
    find: Optional[str] = None
    replace: Optional[str] = None
    mode: Optional[str] = None


class BatchRequest(BaseModel):
    commands: list[BatchCommand]
    stop_on_error: bool = False


class ViewRequest(BaseModel):
    mode: str = "outline"


class MergeRequest(BaseModel):
    data: Optional[dict[str, Any]] = None
    data_file: Optional[str] = None


class GenerateRequest(BaseModel):
    prompt: str
    format: str = Field(..., pattern=r"^(docx|xlsx|pptx)$")
    filename: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    filename: str
    history: list[ChatMessage] = []


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    path: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[dict[str, str]] = None
    results: Any = None
    reply: Optional[str] = None
    actions: Any = None
    issues: list[Any] = []
    resident: Optional[bool] = None
    officecli_version: Optional[str] = None
