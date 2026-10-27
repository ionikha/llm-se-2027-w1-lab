from __future__ import annotations

import json
from io import StringIO

import pytest
from pydantic import ValidationError

from triage import cli
from triage.extract import record_from_prediction
from triage.models import GitHubIssue, TriageRecord


def test_prediction_is_validated_and_identity_comes_from_issue() -> None:
    issue = GitHubIssue.model_validate(
        {
            "number": 12,
            "title": "Incorrect response header",
            "body": "The response has the wrong content type.",
            "html_url": "https://github.com/example/project/issues/12",
        }
    )
    prediction = {
        "repo": "model-chosen-repo",
        "number": 999,
        "url": "https://example.invalid/",
        "summary": "The response content type is incorrect.",
        "issue_type": "bug",
        "component": None,
        "severity": "medium",
        "has_reproduction_steps": False,
        "confidence": 0.84,
        "rationale": "The report describes incorrect behavior.",
    }

    record = record_from_prediction(issue, "example/project", json.dumps(prediction))

    assert record.repo == "example/project"
    assert record.number == 12
    assert record.url == issue.url
    assert record.issue_type == "bug"


def test_triage_record_rejects_out_of_range_confidence() -> None:
    with pytest.raises(ValidationError):
        TriageRecord.model_validate(
            {
                "repo": "example/project",
                "number": 12,
                "url": None,
                "summary": "A short summary.",
                "issue_type": "bug",
                "component": None,
                "severity": "unknown",
                "has_reproduction_steps": False,
                "confidence": 1.2,
                "rationale": "There is little evidence.",
            }
        )


def test_cli_reads_one_issue_from_stdin_and_prints_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    issue_json = {
        "number": 12,
        "title": "Incorrect response header",
        "body": "The response has the wrong content type.",
        "html_url": "https://github.com/example/project/issues/12",
    }
    expected = TriageRecord(
        repo="example/project",
        number=12,
        url="https://github.com/example/project/issues/12",
        summary="The response content type is incorrect.",
        issue_type="bug",
        component=None,
        severity="medium",
        has_reproduction_steps=False,
        confidence=0.84,
        rationale="The report describes incorrect behavior.",
    )

    def fake_triage(issue: GitHubIssue, repository: str) -> TriageRecord:
        assert issue.number == 12
        assert repository == "example/project"
        return expected

    monkeypatch.setattr(cli, "triage_issue", fake_triage)
    monkeypatch.setattr("sys.stdin", StringIO(json.dumps(issue_json)))

    assert cli.main([]) == 0
    assert json.loads(capsys.readouterr().out) == expected.model_dump(mode="json")