# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.data.components import DataDictionary, FewShotBank, FewShotExample, NegativeExample
from coreason_construct.schemas.base import ComponentType


def test_few_shot_bank() -> None:
    """Test FewShotBank construction and rendering."""
    examples = [
        FewShotExample(input="Input 1", output="Output 1"),
        FewShotExample(input="Input 2", output={"key": "value"}),
    ]
    bank = FewShotBank(name="TestBank", examples=examples)

    assert bank.name == "TestBank"
    assert bank.type == ComponentType.DATA
    assert "Input: Input 1" in bank.content
    assert "Ideal Output: Output 1" in bank.content
    assert "Input: Input 2" in bank.content
    assert "{'key': 'value'}" in bank.content
    assert len(bank.examples) == 2


def test_negative_example() -> None:
    """Test NegativeExample construction and rendering."""
    negatives = ["Do not hallucinate.", "Do not use casual language."]
    comp = NegativeExample(name="TestNegatives", examples=negatives)

    assert comp.name == "TestNegatives"
    assert comp.type == ComponentType.DATA
    assert "NEGATIVE CONSTRAINTS" in comp.content
    assert "- Do not hallucinate." in comp.content
    assert "- Do not use casual language." in comp.content


def test_data_dictionary() -> None:
    """Test DataDictionary construction and rendering."""
    terms = {"AE": "Adverse Event", "SAE": "Serious Adverse Event"}
    comp = DataDictionary(name="TestDict", terms=terms)

    assert comp.name == "TestDict"
    assert comp.type == ComponentType.DATA
    assert "DATA DICTIONARY" in comp.content
    assert "AE: Adverse Event" in comp.content
    assert "SAE: Serious Adverse Event" in comp.content
