# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.data.library import AE_Examples
from coreason_construct.schemas.base import ComponentType


def test_ae_examples_structure() -> None:
    """Test the structure of AE_Examples few-shot bank."""
    assert AE_Examples.name == "AE_Examples"
    assert AE_Examples.type == ComponentType.DATA
    assert AE_Examples.priority == 5
    assert len(AE_Examples.examples) == 1


def test_ae_examples_content() -> None:
    """Test that the content of AE_Examples renders correctly."""
    example = AE_Examples.examples[0]
    assert example.input == "Patient reported nausea"
    assert example.output == {"term": "Nausea", "severity": "MILD"}

    rendered = AE_Examples.render()
    assert "Input: Patient reported nausea" in rendered
    assert "Ideal Output: {'term': 'Nausea', 'severity': 'MILD'}" in rendered
