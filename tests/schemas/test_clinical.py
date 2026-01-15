# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from typing import List

import pytest
from pydantic import BaseModel, ValidationError

from coreason_construct.schemas.clinical import AdverseEvent, Causality, Outcome, Severity


def test_adverse_event_valid() -> None:
    """Test creating a valid AdverseEvent."""
    ae = AdverseEvent(
        term="Headache", severity=Severity.MILD, causality=Causality.NOT_RELATED, outcome=Outcome.RECOVERED
    )
    assert ae.term == "Headache"
    assert ae.severity == Severity.MILD
    assert ae.causality == Causality.NOT_RELATED
    assert ae.outcome == Outcome.RECOVERED


def test_adverse_event_defaults() -> None:
    """Test defaults for optional fields."""
    ae = AdverseEvent(term="Nausea", severity=Severity.MODERATE)
    assert ae.term == "Nausea"
    assert ae.severity == Severity.MODERATE
    assert ae.causality is None
    assert ae.outcome is None


def test_adverse_event_string_parsing() -> None:
    """Test that strings are correctly parsed into Enums."""
    ae = AdverseEvent(term="Vomiting", severity="SEVERE")
    assert ae.severity == Severity.SEVERE


def test_adverse_event_invalid_severity() -> None:
    """Test validation error for invalid severity."""
    with pytest.raises(ValidationError) as exc:
        AdverseEvent(term="Pain", severity="EXTREME")
    assert "severity" in str(exc.value)


def test_adverse_event_invalid_causality() -> None:
    """Test validation error for invalid causality."""
    with pytest.raises(ValidationError) as exc:
        AdverseEvent(term="Pain", severity=Severity.MILD, causality="MAYBE")
    assert "causality" in str(exc.value)


def test_adverse_event_empty_term() -> None:
    """Test validation error for empty term string."""
    with pytest.raises(ValidationError) as exc:
        AdverseEvent(term="", severity=Severity.MILD)
    assert "term" in str(exc.value)
    assert "String should have at least 1 character" in str(exc.value)


def test_enum_case_sensitivity() -> None:
    """Test that Enums are case-sensitive (strict)."""
    # Should fail for lowercase "mild"
    with pytest.raises(ValidationError) as exc:
        AdverseEvent(term="Pain", severity="mild")
    assert "severity" in str(exc.value)


def test_complex_batch_parsing() -> None:
    """Test parsing a complex nested structure mimicking LLM output."""

    class PatientSafetyReport(BaseModel):
        patient_id: str
        events: List[AdverseEvent]

    # Simulating JSON output from an LLM
    raw_data = {
        "patient_id": "PT-12345",
        "events": [
            {"term": "Headache", "severity": "MILD", "outcome": "RECOVERED"},
            {"term": "Nausea", "severity": "MODERATE", "causality": "POSSIBLY_RELATED"},
        ],
    }

    report = PatientSafetyReport(**raw_data)

    assert report.patient_id == "PT-12345"
    assert len(report.events) == 2

    evt1 = report.events[0]
    assert evt1.term == "Headache"
    assert evt1.severity == Severity.MILD
    assert evt1.outcome == Outcome.RECOVERED
    assert evt1.causality is None

    evt2 = report.events[1]
    assert evt2.term == "Nausea"
    assert evt2.severity == Severity.MODERATE
    assert evt2.causality == Causality.POSSIBLY_RELATED
    assert evt2.outcome is None
