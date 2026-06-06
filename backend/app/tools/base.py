"""Week 6: Base tool class with LLM-based analysis."""
import abc
from app.tools.result_schema import ToolResult


class BaseTool(abc.ABC):
    @property
    @abc.abstractmethod
    def tool_name(self) -> str: ...

    @abc.abstractmethod
    def analyze(self, data: dict) -> ToolResult:
        """Run analysis given profile/memory/context data. Returns structured result."""
        ...
