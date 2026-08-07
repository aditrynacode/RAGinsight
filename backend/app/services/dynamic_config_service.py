import json
from typing import Dict, Any, List

from app.config import DYNAMIC_CONFIG_PATH

DEFAULT_CONFIG: Dict[str, Any] = {
    "synonym_mappings": {},       # {"cancellation policy": ["notice period", ...]}
    "top_k_overrides": {"default": 4},
    "system_prompt_additions": [],
    "clarification_prompt_additions": [],
}


def get_config() -> Dict[str, Any]:
    if not DYNAMIC_CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    with open(DYNAMIC_CONFIG_PATH, "r") as f:
        config = json.load(f)
    # Backfill any keys added to DEFAULT_CONFIG after this file was first written.
    for key, value in DEFAULT_CONFIG.items():
        config.setdefault(key, value)
    return config


def save_config(config: Dict[str, Any]) -> None:
    with open(DYNAMIC_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def add_synonym_mapping(term: str, aliases: List[str]) -> None:
    config = get_config()
    existing = config["synonym_mappings"].get(term, [])
    config["synonym_mappings"][term] = sorted(set(existing) | set(aliases))
    save_config(config)


def set_top_k(value: int, key: str = "default") -> None:
    config = get_config()
    config["top_k_overrides"][key] = value
    save_config(config)


def add_system_prompt_addition(text: str) -> None:
    config = get_config()
    if text not in config["system_prompt_additions"]:
        config["system_prompt_additions"].append(text)
    save_config(config)


def add_clarification_prompt_addition(text: str) -> None:
    config = get_config()
    if text not in config["clarification_prompt_additions"]:
        config["clarification_prompt_additions"].append(text)
    save_config(config)
