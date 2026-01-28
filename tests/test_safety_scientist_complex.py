# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from unittest.mock import patch

from coreason_construct.contexts.library import HIPAA_Context
from coreason_construct.contexts.registry import CONTEXT_REGISTRY
from coreason_construct.roles.library import SafetyScientist
from coreason_construct.schemas.base import ComponentType
from coreason_construct.weaver import Weaver


from coreason_identity.models import UserContext

def test_safety_scientist_deduplication(mock_context: UserContext) -> None:
    """
    Edge Case: User manually adds a dependency (HIPAA) before adding
    SafetyScientist (which also depends on HIPAA).
    Expectation: HIPAA should appear only once.
    """
    weaver = Weaver()

    # 1. Manually add HIPAA
    weaver.add(HIPAA_Context, context=mock_context)

    # 2. Add SafetyScientist (triggering auto-injection of HIPAA)
    weaver.add(SafetyScientist, context=mock_context)

    # Check counts
    hipaa_count = sum(1 for c in weaver.components if c.name == "HIPAA")
    assert hipaa_count == 1, f"HIPAA should be present exactly once, found {hipaa_count}"

    # Verify SafetyScientist is also there
    assert any(c.name == "SafetyScientist" for c in weaver.components)


def test_safety_scientist_token_resilience(mock_context: UserContext) -> None:
    """
    Complex Scenario: High token pressure.
    SafetyScientist (10) and HIPAA (10) must survive.
    GxP (9) might survive if space permits.
    Low priority data (e.g. priority 1) should be dropped first.
    """
    weaver = Weaver()
    weaver.add(SafetyScientist, context=mock_context)  # Adds HIPAA(10), GxP(9)

    # Add a low priority massive component
    from coreason_construct.schemas.base import PromptComponent

    massive_content = "x" * 1000
    low_prio = PromptComponent(name="LowPrioJunk", type=ComponentType.DATA, content=massive_content, priority=1)
    weaver.add(low_prio, context=mock_context)

    # SafetyScientist content ~300 chars? HIPAA ~200? GxP ~150?
    # Total essentials < 1000 chars.
    # Total with junk ~ 2000 chars.
    # Set limit to allow essentials but kill junk.
    # Weaver estimates 4 chars/token.
    # Let's say we allow 300 tokens (1200 chars).

    config = weaver.build(user_input="Test", max_tokens=300, context=mock_context)

    # Verify LowPrioJunk is gone
    assert "LowPrioJunk" not in config.system_message

    # Verify SafetyScientist and HIPAA are present (Priority 10)
    assert "Safety Scientist" in config.system_message or "SafetyScientist" in config.provenance_metadata["role"]
    assert "HIPAA" in config.system_message

    # GxP (9) might be there or not depending on exact math, but Priority 10 MUST be there.
    # Since SafetyScientist(10) > GxP(9), GxP would be dropped before SafetyScientist.


def test_safety_scientist_missing_dependency(mock_context: UserContext) -> None:
    """
    Edge Case: A required dependency (GxP) is missing from the registry.
    Expectation: Weaver warns but proceeds; SafetyScientist is added, GxP is not.
    """
    # Create a copy of the registry without GxP
    mock_registry = dict(CONTEXT_REGISTRY)
    if "GxP" in mock_registry:
        del mock_registry["GxP"]

    # Patch the registry where ContextLibrary finds it
    with patch("coreason_construct.contexts.registry.CONTEXT_REGISTRY", mock_registry):
        weaver = Weaver()
        weaver.add(SafetyScientist, context=mock_context)

        # SafetyScientist should be added
        assert any(c.name == "SafetyScientist" for c in weaver.components)

        # HIPAA (still in registry) should be added
        assert any(c.name == "HIPAA" for c in weaver.components)

        # GxP (removed from registry) should NOT be added
        assert not any(c.name == "GxP" for c in weaver.components)


def test_full_pv_workflow_assembly(mock_context: UserContext) -> None:
    """
    Complex Scenario: Full assembly with Role, Dynamic Context, and Task.
    """
    weaver = Weaver(context_data={"patient_id": "PT-001"})

    # 1. Add Role
    weaver.add(SafetyScientist, context=mock_context)

    # 2. Add Dynamic Context
    # Weaver resolves "PatientHistory" from registry using context_data
    # Note: resolving via name string requires it to be in registry
    patient_history = CONTEXT_REGISTRY["PatientHistory"](patient_id="PT-001")  # type: ignore
    weaver.add(patient_history, context=mock_context)

    # 3. Build Prompt
    user_input = "Patient experienced nausea."
    config = weaver.build(user_input, context=mock_context)

    system_msg = config.system_message

    # Assertions
    assert "Senior Safety Scientist" in system_msg  # Role Title
    assert "HIPAA" in system_msg  # Dependency
    assert "Patient History for ID: PT-001" in system_msg  # Dynamic Context
    assert "Patient experienced nausea" in config.user_message

    # Metadata check
    assert config.provenance_metadata["role"] == "SafetyScientist"
