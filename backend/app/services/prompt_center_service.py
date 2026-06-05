"""Prompt Center Service — unified prompt management with version tracking.

Loads prompt templates from prompts/ directory, caches them in memory,
and tracks versions for audit/debugging purposes.
"""
import os
from pathlib import Path
from functools import lru_cache

# Prompt version mapping: name -> (path, version)
PROMPT_REGISTRY = {
    "system_base": ("prompts/global/system_base_prompt.md", "v1"),
    "psychology": ("prompts/nodes/psychology_prompt.md", "v1"),
    "tarot": ("prompts/nodes/tarot_prompt.md", "v1"),
    "compatibility": ("prompts/scenes/compatibility_prompt.md", "v1"),
    "intent_router": ("prompts/nodes/intent_router_prompt.md", "v1"),
    "entity_extractor": ("prompts/nodes/entity_extractor_prompt.md", "v1"),
    "event_detector": ("prompts/nodes/event_detector_prompt.md", "v1"),
    "memory_update": ("prompts/nodes/memory_update_prompt.md", "v1"),
    "report_builder": ("prompts/nodes/report_builder_prompt.md", "v1"),
    "general_guidance": ("prompts/scenes/general_guidance_prompt.md", "v1"),
    "relationship_analysis": ("prompts/scenes/relationship_analysis_prompt.md", "v1"),
}


class PromptCenterService:
    """Centralized prompt management service."""

    def __init__(self, base_dir: str | None = None) -> None:
        if base_dir is None:
            # Resolve relative to this file: app/services/ -> ../../  -> project root
            base_dir = str(Path(__file__).resolve().parents[3])
        self.base_dir = base_dir
        self._cache: dict[str, tuple[str, str]] = {}
        self.versions: dict[str, str] = {name: ver for name, (_, ver) in PROMPT_REGISTRY.items()}

    def get(self, name: str) -> str:
        """Get prompt content by name. Loads from file and caches."""
        if name in self._cache:
            cached_content, cached_version = self._cache[name]
            current_version = self.versions.get(name, "unknown")
            if cached_version == current_version:
                return cached_content

        if name not in PROMPT_REGISTRY:
            raise KeyError(f"Prompt '{name}' not found in registry. Available: {list(PROMPT_REGISTRY.keys())}")

        rel_path, version = PROMPT_REGISTRY[name]
        full_path = os.path.join(self.base_dir, rel_path)

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except FileNotFoundError:
            raise RuntimeError(f"Prompt file not found: {full_path}")

        self._cache[name] = (content, version)
        return content

    def get_or_default(self, name: str, default: str) -> str:
        try:
            return self.get(name)
        except Exception:
            return default

    def get_version(self, name: str) -> str:
        return self.versions.get(name, "unknown")

    def list_prompts(self) -> dict[str, str]:
        """Return all prompt names with their versions."""
        return dict(self.versions)

    def clear_cache(self) -> None:
        self._cache.clear()

    @staticmethod
    def render(prompt_template: str, **kwargs) -> str:
        """Simple template rendering with {key} substitution."""
        result = prompt_template
        for key, value in kwargs.items():
            result = result.replace("{" + key + "}", str(value))
        return result


# Singleton for easy access
_prompt_center: PromptCenterService | None = None


def get_prompt_center() -> PromptCenterService:
    global _prompt_center
    if _prompt_center is None:
        _prompt_center = PromptCenterService()
    return _prompt_center
