import os
import tempfile
import shutil
from pathlib import Path
from git import Repo

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h",
    ".go", ".rs", ".rb", ".php", ".cs", ".md", ".txt",
    ".yaml", ".yml", ".toml", ".json", ".sh", ".env.example"
}

IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "coverage"
}

def load_repo(repo_url: str) -> list[dict]:
    """Clone repo, read all supported files, return list of {path, content}"""
    tmp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning {repo_url}...")
        Repo.clone_from(repo_url, tmp_dir, depth=1)
        files = []
        for root, dirs, filenames in os.walk(tmp_dir):
            # prune ignored dirs in place
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for filename in filenames:
                ext = Path(filename).suffix.lower()
                if ext in SUPPORTED_EXTENSIONS:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, tmp_dir)
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        if content.strip():  # skip empty files
                            files.append({
                                "path": rel_path.replace("\\", "/"),
                                "content": content
                            })
                    except Exception:
                        continue
        print(f"Loaded {len(files)} files from repo.")
        return files
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)