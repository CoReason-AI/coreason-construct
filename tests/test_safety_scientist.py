# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.roles.library import SafetyScientist
from coreason_construct.weaver import Weaver


def test_safety_scientist_dependency_injection() -> None:
    """
    Test that adding the SafetyScientist role to the Weaver
    automatically injects its dependencies (HIPAA, GxP).
    """
    weaver = Weaver()
    weaver.add(SafetyScientist)

    # Check that SafetyScientist is present
    assert any(c.name == "SafetyScientist" for c in weaver.components)

    # Check that HIPAA is present (injected dependency)
    assert any(c.name == "HIPAA" for c in weaver.components)

    # Check that GxP is present (injected dependency)
    assert any(c.name == "GxP" for c in weaver.components)


def test_safety_scientist_priority() -> None:
    """
    Test that SafetyScientist has Critical priority (10).
    """
    assert SafetyScientist.priority == 10
