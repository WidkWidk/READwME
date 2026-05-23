"""配置模块"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(env_prefix="RC_")

    app_name: str = "Reading Companion"
    vault_path: Path = Path("./vault")
    db_path: Path = Path("./data/reading.db")
    dict_api_base: str = "https://api.dictionaryapi.dev/api/v2/entries/en"
    dict_timeout: float = 5.0

    # LLM 配置（不使用 RC_ 前缀，直接读取环境变量）
    llm_base_url: str = "https://www.packyapi.com/v1"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.7

    def model_post_init(self, __context) -> None:
        """初始化后从无前缀环境变量读取 LLM 配置"""
        if not self.llm_api_key:
            # 优先读 LLM_API_KEY，其次 ANTHROPIC_API_KEY
            key = os.environ.get("LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
            object.__setattr__(self, "llm_api_key", key)
        if os.environ.get("LLM_BASE_URL"):
            object.__setattr__(self, "llm_base_url", os.environ["LLM_BASE_URL"])
        if os.environ.get("LLM_MODEL"):
            object.__setattr__(self, "llm_model", os.environ["LLM_MODEL"])


settings = Settings()
