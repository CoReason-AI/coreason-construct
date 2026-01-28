# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from typing import Any

from pytest import CaptureFixture

from coreason_construct.contexts.registry import CONTEXT_REGISTRY
from coreason_construct.roles.base import RoleDefinition
from coreason_construct.schemas.base import PromptComponent
from coreason_construct.weaver import Weaver


def test_dynamic_dependency_injection(mock_context) -> None:
    """
    Test that a Role depending on a dynamic context (PatientHistory)
    is correctly resolved when context_data is provided.
    """
    # 1. Define a Role that depends on PatientHistory
    DoctorRole = RoleDefinition(
        name="Doctor",
        title="Doctor",
        tone="Professional",
        competencies=["Medicine"],
        dependencies=["PatientHistory"],  # Dynamic dependency
    )

    # 2. Initialize Weaver with required data
    weaver = Weaver(context_data={"patient_id": "P12345"})

    # 3. Add the Role
    weaver.add(DoctorRole, context=mock_context)

    # 4. Verify that PatientHistory_P12345 was added
    # The name is dynamically generated as "PatientHistory_{patient_id}"
    patient_history = next((c for c in weaver.components if c.name == "PatientHistory_P12345"), None)

    assert patient_history is not None, "PatientHistory should be injected"
    assert "P12345" in patient_history.content


def test_dynamic_dependency_missing_data(mock_context) -> None:
    """
    Test that missing context data logs a warning and does not crash,
    and the dependency is NOT added.
    """
    DoctorRole = RoleDefinition(
        name="Doctor",
        title="Doctor",
        tone="Professional",
        competencies=["Medicine"],
        dependencies=["PatientHistory"],
    )

    # No patient_id provided
    weaver = Weaver(context_data={})
    weaver.add(DoctorRole, context=mock_context)

    # Verify PatientHistory is NOT added
    patient_history_components = [c for c in weaver.components if c.name.startswith("PatientHistory")]
    assert len(patient_history_components) == 0, "PatientHistory should not be added if data is missing"


def test_mixed_dependencies(mock_context) -> None:
    """
    Test that Weaver handles both static (HIPAA) and dynamic (StudyProtocol) dependencies.
    """
    # Role depends on both
    LeadInvestigator = RoleDefinition(
        name="LeadInvestigator",
        title="Lead Investigator",
        tone="Professional",
        competencies=["Clinical Trials"],
        dependencies=["HIPAA", "StudyProtocol"],
    )

    weaver = Weaver(context_data={"nct_id": "NCT0001"})
    weaver.add(LeadInvestigator, context=mock_context)

    # Check HIPAA (static)
    has_hipaa = any(c.name == "HIPAA" for c in weaver.components)
    assert has_hipaa, "HIPAA should be injected"

    # Check StudyProtocol (dynamic)
    study_protocol = next((c for c in weaver.components if c.name == "StudyProtocol_NCT0001"), None)
    assert study_protocol is not None, "StudyProtocol should be injected"
    assert "NCT0001" in study_protocol.content


class BrokenComponent(PromptComponent):
    """A component that raises an error during init."""

    def __init__(self, **data: Any):
        raise ValueError("I am broken")


def test_dynamic_dependency_instantiation_failure(capsys: CaptureFixture[Any], mock_context) -> None:
    """
    Test that if instantiation raises an exception, it is caught and logged.
    """
    import sys

    from loguru import logger

    # 1. Register broken component
    CONTEXT_REGISTRY["BrokenComp"] = BrokenComponent

    # 2. Setup logger capture
    handler_id = logger.add(sys.stderr, level="ERROR")

    # 3. Call _resolve_dependency directly
    weaver = Weaver()
    result = weaver._resolve_dependency("BrokenComp", context=mock_context)

    # 4. Cleanup
    del CONTEXT_REGISTRY["BrokenComp"]
    logger.remove(handler_id)

    # 5. Verify error log
    captured = capsys.readouterr()
    assert "Failed to instantiate dependency 'BrokenComp': I am broken" in captured.err

    # 6. Verify result is None
    assert result is None
