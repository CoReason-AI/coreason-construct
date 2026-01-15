# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

import pytest
from pydantic import ValidationError

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
