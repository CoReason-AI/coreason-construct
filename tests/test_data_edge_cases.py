# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.data.components import FewShotBank, FewShotExample


def test_few_shot_braces_in_input() -> None:
    """Test that input containing curly braces does not cause KeyError."""
    bank = FewShotBank(
        name="BraceInput",
        examples=[
            FewShotExample(input="Patient said {foo}", output="bar"),
        ],
    )
    rendered = bank.render()
    assert "Input: Patient said {foo}" in rendered
    assert "Ideal Output: bar" in rendered


def test_few_shot_nested_output() -> None:
    """Test that nested dictionary output renders correctly."""
    bank = FewShotBank(
        name="NestedOutput",
        examples=[
            FewShotExample(input="Input", output={"key": {"nested": "value"}}),
        ],
    )
    rendered = bank.render()
    assert "Ideal Output: {'key': {'nested': 'value'}}" in rendered


def test_few_shot_multiple_examples() -> None:
    """Test rendering of multiple examples."""
    bank = FewShotBank(
        name="MultiExample",
        examples=[
            FewShotExample(input="In1", output="Out1"),
            FewShotExample(input="In2", output="Out2"),
        ],
    )
    rendered = bank.render()
    assert "Input: In1" in rendered
    assert "Ideal Output: Out1" in rendered
    assert "Input: In2" in rendered
    assert "Ideal Output: Out2" in rendered
