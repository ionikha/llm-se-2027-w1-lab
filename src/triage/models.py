"""Validated input and output models for issue triage."""

from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class GitHubIssue(BaseModel):
    """The subset of a GitHub issue payload needed for triage."""

    model_config = ConfigDict(extra="ignore")

    repo: str | None = None
    number: int = Field(validation_alias=AliasChoices("number", "issue_number"))
    title: str
    body: str | None = None
    url: str | None = Field(
        default=None, validation_alias=AliasChoices("html_url", "url")
    )


class TriageRecord(BaseModel):
    """One validated triage result; it does not decide a destination queue."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    repo: str
    number: int
    url: str | None
    summary: str = Field(min_length=1)
    issue_type: Literal[
        "bug", "enhancement", "documentation", "question", "meta", "unknown"
    ]
    component: str | None
    severity: Literal["low", "medium", "high", "critical", "unknown"]
    has_reproduction_steps: bool
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=1)