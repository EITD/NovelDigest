from dataclasses import dataclass
from typing import Dict, Any
import json
import os


@dataclass
class Novel:
    jj: str
    jj_page: int
    cp: str
    cp_page: int
    prompt: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Novel":
        return cls(
            jj=data.get("jj", ""),
            jj_page=data.get("jj_page", 3),
            cp=data.get("cp", ""),
            cp_page=data.get("cp_page", 10),
            prompt=data.get("prompt", ""),
        )


def load_data(path: str = None) -> Dict[str, Novel]:
    """Load novel data from NOVEL_JSON env var or novel.json file."""
    env_json = os.getenv("NOVEL_JSON")
    if env_json:
        raw = json.loads(env_json)
    else:
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "novel.json")
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)

    novels: Dict[str, Novel] = {}
    for k, v in raw.items():
        novels[str(k)] = Novel.from_dict(v)

    return novels

__all__ = ["Novel", "load_data"]
