import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from agent.tools.registry import registry
from agent.security.permissions import RiskLevel

# 1. create_file
@registry.register(
    name="create_file",
    description="Create a file at specified path with optional initial content.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target file path"},
            "content": {"type": "string", "description": "File content"}
        },
        "required": ["path"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="filesystem.write",
    verify_func=lambda result, **kwargs: os.path.isfile(kwargs.get("path", ""))
)
async def create_file(path: str, content: str = "") -> Dict[str, Any]:
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return {"success": True, "path": str(p), "bytes_written": len(content)}

# 2. read_file
@registry.register(
    name="read_file",
    description="Read content from a specified file path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target file path"}
        },
        "required": ["path"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="filesystem.read"
)
async def read_file(path: str) -> Dict[str, Any]:
    p = Path(path).resolve()
    if not p.exists() or not p.is_file():
        return {"success": False, "error": f"File not found: {path}"}
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return {"success": True, "path": str(p), "content": content}

# 3. write_file
@registry.register(
    name="write_file",
    description="Overwrite content of an existing file.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target file path"},
            "content": {"type": "string", "description": "Content to write"}
        },
        "required": ["path", "content"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="filesystem.write",
    verify_func=lambda result, **kwargs: os.path.isfile(kwargs.get("path", ""))
)
async def write_file(path: str, content: str) -> Dict[str, Any]:
    p = Path(path).resolve()
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return {"success": True, "path": str(p), "bytes_written": len(content)}

# 4. copy_file
@registry.register(
    name="copy_file",
    description="Copy file from source path to destination path.",
    parameters={
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Source path"},
            "destination": {"type": "string", "description": "Destination path"}
        },
        "required": ["source", "destination"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="filesystem.write",
    verify_func=lambda result, **kwargs: os.path.exists(kwargs.get("destination", ""))
)
async def copy_file(source: str, destination: str) -> Dict[str, Any]:
    src, dst = Path(source).resolve(), Path(destination).resolve()
    if not src.exists():
        return {"success": False, "error": f"Source path does not exist: {source}"}
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)
    return {"success": True, "source": str(src), "destination": str(dst)}

# 5. move_file
@registry.register(
    name="move_file",
    description="Move or rename file/folder from source to destination.",
    parameters={
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Source path"},
            "destination": {"type": "string", "description": "Destination path"}
        },
        "required": ["source", "destination"]
    },
    risk_level=RiskLevel.DANGEROUS,
    required_permission="filesystem.write",
    verify_func=lambda result, **kwargs: os.path.exists(kwargs.get("destination", ""))
)
async def move_file(source: str, destination: str) -> Dict[str, Any]:
    src, dst = Path(source).resolve(), Path(destination).resolve()
    if not src.exists():
        return {"success": False, "error": f"Source path does not exist: {source}"}
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dst)
    return {"success": True, "source": str(src), "destination": str(dst)}

# 6. delete_file
@registry.register(
    name="delete_file",
    description="Delete a file or folder path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target path to delete"}
        },
        "required": ["path"]
    },
    risk_level=RiskLevel.DANGEROUS,
    required_permission="filesystem.delete",
    verify_func=lambda result, **kwargs: not os.path.exists(kwargs.get("path", ""))
)
async def delete_file(path: str) -> Dict[str, Any]:
    p = Path(path).resolve()
    if not p.exists():
        return {"success": True, "message": "Path already absent", "path": str(p)}
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()
    return {"success": True, "path": str(p)}

# 7. create_folder
@registry.register(
    name="create_folder",
    description="Create a directory path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target folder path"}
        },
        "required": ["path"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="filesystem.write",
    verify_func=lambda result, **kwargs: os.path.isdir(kwargs.get("path", ""))
)
async def create_folder(path: str) -> Dict[str, Any]:
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return {"success": True, "path": str(p)}

# 8. search_files
@registry.register(
    name="search_files",
    description="Search for files matching query inside a directory path.",
    parameters={
        "type": "object",
        "properties": {
            "directory": {"type": "string", "description": "Directory to search in"},
            "pattern": {"type": "string", "description": "Glob pattern, e.g. *.txt or *project*"}
        },
        "required": ["directory", "pattern"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="filesystem.read"
)
async def search_files(directory: str, pattern: str) -> Dict[str, Any]:
    p = Path(directory).resolve()
    if not p.exists() or not p.is_dir():
        return {"success": False, "error": f"Directory not found: {directory}"}
    matches = [str(f) for f in p.rglob(pattern)]
    return {"success": True, "directory": str(p), "matches": matches[:100]}

# 9. list_directory
@registry.register(
    name="list_directory",
    description="List contents of a directory path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target folder path"}
        },
        "required": ["path"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="filesystem.read"
)
async def list_directory(path: str) -> Dict[str, Any]:
    p = Path(path).resolve()
    if not p.exists() or not p.is_dir():
        return {"success": False, "error": f"Directory not found: {path}"}
    items = []
    for item in p.iterdir():
        items.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else 0
        })
    return {"success": True, "path": str(p), "items": items}
