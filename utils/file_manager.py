"""
文件管理工具
处理上传文件的保存、临时存储和输出文件管理
"""
import os
import uuid
from pathlib import Path
from typing import Optional


class FileManager:
    """管理临时文件存储"""

    def __init__(self, base_temp_dir: str = "./temp"):
        self.base_temp_dir = Path(base_temp_dir)
        self.base_temp_dir.mkdir(parents=True, exist_ok=True)

    def create_session_dir(self, session_id: str) -> Path:
        """为session创建专属目录"""
        session_dir = self.base_temp_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def save_uploaded_file(self, uploaded_file, session_id: str) -> str:
        """
        保存上传的文件到临时目录

        Args:
            uploaded_file: Streamlit上传的文件对象
            session_id: 会话ID

        Returns:
            保存后的文件路径
        """
        session_dir = self.create_session_dir(session_id)
        file_path = session_dir / uploaded_file.name

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        return str(file_path)

    def generate_output_filename(self, original_path: str, suffix: str = "_colored") -> str:
        """
        生成输出文件名

        Args:
            original_path: 原始文件路径
            suffix: 文件名后缀

        Returns:
            新文件路径
        """
        path = Path(original_path)
        new_name = f"{path.stem}{suffix}{path.suffix}"
        return str(path.parent / new_name)

    def cleanup_session(self, session_id: str):
        """清理session的临时文件"""
        session_dir = self.base_temp_dir / session_id
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)

    def get_session_files(self, session_id: str) -> list:
        """获取session下的所有文件"""
        session_dir = self.base_temp_dir / session_id
        if not session_dir.exists():
            return []
        return [str(f) for f in session_dir.iterdir() if f.is_file()]
