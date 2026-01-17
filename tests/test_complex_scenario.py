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
from coreason_construct.primitives.extract import ExtractionPrimitive
from coreason_construct.schemas.clinical import AdverseEvent
from coreason_construct.weaver import Weaver


def test_complex_clinical_scenario() -> None:
    """
    Test a complex scenario with:
    - Long clinical text with special characters.
    - Complex structured output (simulated).
    """
    complex_input = (
        "Patient presented with 'severe' headache (VAS 8/10) & nausea.\n"
        "Notes: {Observation}: Symptoms started 2 hours after administration."
    )

    complex_output = {
        "term": "Headache",
        "severity": "SEVERE",
        "notes": "Patient reported VAS 8/10",
    }

    bank = FewShotBank(
        name="ComplexBank",
        examples=[
            FewShotExample(input=complex_input, output=complex_output),
        ],
    )

    weaver = Weaver()
    weaver.add(bank)
    weaver.add(ExtractionPrimitive(name="ComplexExtractor", schema=AdverseEvent))

    config = weaver.build(user_input="Test input")

    # Verification
    # Ensure the braces in input "{Observation}" were escaped and rendered correctly
    assert "{Observation}" in config.system_message
    # Ensure special chars like newlines are preserved
    assert "VAS 8/10" in config.system_message
    # Ensure output structure is preserved
    assert "'term': 'Headache'" in config.system_message
