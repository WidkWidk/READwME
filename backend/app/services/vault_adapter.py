"""Obsidian Vault 读写适配器"""

from pathlib import Path

from app.config import settings


class VaultAdapter:
    """Obsidian Vault 文件操作"""

    def __init__(self, vault_path: Path | None = None):
        self.vault_path = vault_path or settings.vault_path
        self.reading_path = self.vault_path / "Reading"
        self.reading_path.mkdir(parents=True, exist_ok=True)

    def _session_dir(self, title: str) -> Path:
        """获取 session 对应的目录"""
        return self.reading_path / title

    def create_session_folder(self, title: str) -> Path:
        """创建 session 对应的文件夹结构"""
        session_dir = self._session_dir(title)
        session_dir.mkdir(parents=True, exist_ok=True)
        source_dir = session_dir / "_source"
        source_dir.mkdir(exist_ok=True)
        return session_dir

    def get_source_dir(self, title: str) -> Path:
        """获取 session 的源文件目录"""
        return self._session_dir(title) / "_source"

    def write_note(self, title: str, filename: str, content: str) -> Path:
        """写入 markdown 笔记"""
        session_dir = self._session_dir(title)
        session_dir.mkdir(parents=True, exist_ok=True)
        note_path = session_dir / filename
        note_path.write_text(content, encoding="utf-8")
        return note_path

    def read_note(self, title: str, filename: str) -> str:
        """读取笔记内容"""
        note_path = self._session_dir(title) / filename
        if not note_path.exists():
            raise FileNotFoundError(f"笔记不存在: {filename}")
        return note_path.read_text(encoding="utf-8")

    def list_notes(self, title: str) -> list[str]:
        """列出 session 下所有笔记文件"""
        session_dir = self._session_dir(title)
        if not session_dir.exists():
            return []
        return [
            f.name for f in session_dir.iterdir()
            if f.is_file() and f.suffix == ".md"
        ]
