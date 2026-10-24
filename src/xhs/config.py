"""读取 config/ 和 prompts/ 下的文件。改配置不需要改代码。"""
import os
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(os.environ.get("XHS_ROOT", Path(__file__).resolve().parents[2]))
CONFIG = ROOT / "config"
PROMPTS = ROOT / "prompts"


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    with open(CONFIG / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def settings() -> dict:
    return load("settings")


def prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


def data_dir() -> Path:
    p = ROOT / settings()["paths"]["data"]
    p.mkdir(parents=True, exist_ok=True)
    return p


def issue_dir(issue_no: int) -> Path:
    p = data_dir() / "issues" / f"{issue_no:03d}"
    p.mkdir(parents=True, exist_ok=True)
    return p
