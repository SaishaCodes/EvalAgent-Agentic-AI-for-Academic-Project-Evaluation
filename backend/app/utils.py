# backend/app/utils.py
import zipfile, tempfile, os, pathlib
from typing import Tuple

def unzip_to_temp(zip_bytes: bytes) -> Tuple[str, str]:
    """
    Returns (temp_dir_path, top_level_folder_name)
    The temp dir is automatically cleaned up by the caller (use context manager).
    """
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "upload.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(temp_dir)

    # Detect the folder that contains the project (ignore __MACOSX, etc.)
    entries = [p for p in os.listdir(temp_dir) if not p.startswith("__MACOSX")]
    if len(entries) == 1 and os.path.isdir(os.path.join(temp_dir, entries[0])):
        project_root = os.path.join(temp_dir, entries[0])
    else:
        project_root = temp_dir
    return temp_dir, project_root

def read_file(root: str, relative_path: str) -> str:
    fp = pathlib.Path(root) / relative_path
    if not fp.is_file():
        return ""
    return fp.read_text(encoding="utf8", errors="ignore")