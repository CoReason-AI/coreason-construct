# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.contexts.library import GxP_Context
from coreason_construct.primitives.summarize import SummarizationPrimitive
from coreason_construct.roles.library import MedicalDirector
from coreason_construct.schemas.primitives import Summary
from coreason_construct.weaver import Weaver


def test_weaver_dependency_resolution(mock_context) -> None:
    """Test that MedicalDirector role triggers HIPAA context injection."""
    weaver = Weaver()
    weaver.add(MedicalDirector, context=mock_context)

    component_names = [c.name for c in weaver.components]
    assert "MedicalDirector" in component_names
    assert "HIPAA" in component_names


def test_weaver_build_flow(mock_context) -> None:
    """Test the full build flow with multiple components."""
    weaver = Weaver()
    weaver.add(MedicalDirector, context=mock_context)
    weaver.add(GxP_Context, context=mock_context)
    primitive = SummarizationPrimitive()
    weaver.add(primitive, context=mock_context)

    config = weaver.build(user_input="Patient X has diabetes.", variables={}, context=mock_context)

    # Check System Message
    assert "You are a Medical Director" in config.system_message
    assert "HIPAA regulations" in config.system_message
    assert "GxP guidelines" in config.system_message

    # Check User Message
    assert "Summarize the input text" in config.user_message
    assert "INPUT DATA:" in config.user_message
    assert "Patient X has diabetes." in config.user_message

    # Check Response Model
    assert config.response_model == Summary

    # Check Provenance
    assert config.provenance_metadata["role"] == "MedicalDirector"
    assert config.provenance_metadata["schema"] == "Summary"


def test_weaver_sorting(mock_context) -> None:
    """Test that components are sorted by priority."""
    weaver = Weaver()

    # Add in random order
    weaver.add(GxP_Context, context=mock_context)  # Priority 9
    weaver.add(MedicalDirector, context=mock_context)  # Priority 10

    # HIPAA (Priority 10) is auto-added by MedicalDirector

    sorted_comps = weaver._sort_components(weaver.components)

    # Expecting priorities: 10, 10, 9
    priorities = [c.priority for c in sorted_comps]
    assert priorities == [10, 10, 9]

    # Check specifically that MedicalDirector (10) and HIPAA (10) are before GxP (9)
    # The order between MedicalDirector and HIPAA depends on insertion order and stable sort.
    # New Logic: Role is added to list first, then dependencies.
    # So MedicalDirector is added before HIPAA.
    # Stable sort preserves this.

    assert sorted_comps[0].name == "MedicalDirector"
    assert sorted_comps[1].name == "HIPAA"
    assert sorted_comps[2].name == "GxP"


def test_weaver_build_defaults() -> None:
    """Test build with default arguments."""
    weaver = Weaver()
    # Should not raise error when variables is None (default)
    config = weaver.build(user_input="Test input")
    assert config.user_message == "Test input"


def test_weaver_duplicate_add_early_exit(mock_context) -> None:
    """Test that adding the same component twice returns early."""
    weaver = Weaver()
    weaver.add(MedicalDirector, context=mock_context)

    initial_count = len(weaver.components)

    # Add again
    weaver.add(MedicalDirector, context=mock_context)

    assert len(weaver.components) == initial_count
