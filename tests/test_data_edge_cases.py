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


def test_few_shot_bank_input_braces() -> None:
    """
    Test that inputs containing curly braces do not cause formatting errors.
    """
    example = FewShotExample(input="Patient reported {severe} pain.", output="Extraction")
    bank = FewShotBank(name="BraceInputBank", examples=[example])

    # Should render without KeyError despite {severe} looking like a format key
    content = bank.render()
    assert "Input: Patient reported {severe} pain." in content


def test_few_shot_bank_nested_structure() -> None:
    """
    Test that complex nested dictionary outputs are rendered correctly.
    """
    output_data = {
        "events": [
            {"term": "Nausea", "meta": {"duration": "2h"}},
            {"term": "Vomiting", "meta": {"duration": "1h"}},
        ]
    }
    example = FewShotExample(input="Complex Case", output=output_data)
    bank = FewShotBank(name="NestedBank", examples=[example])

    content = bank.render()
    # Check if nested structure is preserved in string representation
    assert "'term': 'Nausea'" in content
    assert "'duration': '2h'" in content
    assert "[{'term':" in content


def test_few_shot_bank_empty() -> None:
    """
    Test behavior with no examples.
    """
    bank = FewShotBank(name="EmptyBank", examples=[])
    content = bank.render()
    assert "Here are some examples of how to perform the task:" in content
    # Should end there or have empty lines
    assert content.strip().endswith("task:")
