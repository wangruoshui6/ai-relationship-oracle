"""Week 6: Unified tool result schema."""
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    tool: str = Field(..., description="Tool name: bazi / psychology / tarot")
    status: str = Field(default="ok", description="ok / degraded / unavailable")
    core_signals: list[str] = Field(default_factory=list, description="Key findings in 1-3 words each")
    risks: list[str] = Field(default_factory=list, description="Potential risks or concerns")
    opportunities: list[str] = Field(default_factory=list, description="Positive signals or growth areas")
    actions: list[str] = Field(default_factory=list, description="Concrete actionable suggestions")
    confidence_notes: str | None = Field(default=None, description="Caveats about data completeness")


class StructuredResult(BaseModel):
    tool_results: list[ToolResult] = Field(default_factory=list)
    summary: str | None = Field(default=None, description="Aggregated analysis brief for the LLM prompt")
