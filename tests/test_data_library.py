# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.data.components import FewShotBank
from coreason_construct.data.library import AE_Examples


def test_ae_examples_structure() -> None:
    """
    Test that AE_Examples is correctly structured as a FewShotBank.
    """
    assert isinstance(AE_Examples, FewShotBank)
    assert AE_Examples.name == "AE_Examples"
    assert AE_Examples.priority == 5
    assert len(AE_Examples.examples) == 2


def test_ae_examples_content() -> None:
    """
    Test the content of the examples in AE_Examples.
    """
    # Example 1
    ex1 = AE_Examples.examples[0]
    assert ex1.input == "Patient reported mild nausea."
    assert ex1.output == {"term": "Nausea", "severity": "MILD", "causality": None, "outcome": None}

    # Example 2
    ex2 = AE_Examples.examples[1]
    assert ex2.input == "Subject died due to cardiac arrest, unrelated to study treatment."
    assert ex2.output == {
        "term": "Cardiac Arrest",
        "severity": "FATAL",
        "causality": "NOT_RELATED",
        "outcome": "FATAL",
    }


def test_ae_examples_rendering() -> None:
    """
    Test that the AE_Examples component renders its content string correctly.
    """
    content = AE_Examples.render()

    # Check header
    assert "Here are some examples of how to perform the task:" in content

    # Check Example 1 presence
    assert "Input: Patient reported mild nausea." in content
    assert "'term': 'Nausea'" in content
    assert "'severity': 'MILD'" in content

    # Check Example 2 presence
    assert "Input: Subject died due to cardiac arrest" in content
    assert "'term': 'Cardiac Arrest'" in content
    assert "'severity': 'FATAL'" in content
    assert "'causality': 'NOT_RELATED'" in content
