from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SkillMatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    skill: str = Field(min_length=1, max_length=120)
    requirement_quote: str = Field(min_length=3, max_length=800)
    required: bool
    status: Literal["strong", "partial", "missing"]
    evidence: str | None = Field(default=None, max_length=1200)
    explanation: str = Field(min_length=10, max_length=1600)


class Suggestion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    original: str = Field(min_length=5, max_length=1200)
    rewrite: str = Field(min_length=5, max_length=1600)
    reason: str = Field(min_length=5, max_length=800)


class ModelAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    summary: str = Field(min_length=10, max_length=2000)
    skills: list[SkillMatch] = Field(min_length=1, max_length=25)
    suggestions: list[Suggestion] = Field(max_length=6)
