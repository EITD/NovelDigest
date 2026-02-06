from dataclasses import dataclass
from typing import Dict, Any
import json
import os


@dataclass
class Novel:
    jj: str
    cp: str
    prompt: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Novel":
        return cls(
            jj=data.get("jj", ""),
            cp=data.get("cp", ""),
            prompt=data.get("prompt", ""),
        )


def load_data(path: str = None) -> Dict[str, Novel]:
    """Load novel data from NOVEL_JSON env var or novel.json file."""
    env_json = os.environ.get("NOVEL_JSON")
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
