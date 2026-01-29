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

from coreason_construct.contexts.library import HIPAA_Context
from coreason_identity.models import UserContext

from coreason_construct.roles.library import Biostatistician, MedicalDirector
from coreason_construct.weaver import Weaver


def test_weaver_auto_dependency_medical_director(mock_context) -> None:
    """Test that adding MedicalDirector automatically injects HIPAA context."""
    weaver = Weaver()
    weaver.add(MedicalDirector, context=mock_context)

    # Check if HIPAA context is present
    has_hipaa = any(c.name == "HIPAA" for c in weaver.components)
    assert has_hipaa, "HIPAA context should be automatically injected for MedicalDirector"


def test_weaver_no_dependency_biostatistician(mock_context) -> None:
    """Test that adding Biostatistician does NOT inject HIPAA (unless configured)."""
    weaver = Weaver()
    weaver.add(Biostatistician, context=mock_context)

    # Check if HIPAA context is NOT present (Biostatistician doesn't have it in dependencies yet)
    has_hipaa = any(c.name == "HIPAA" for c in weaver.components)
    assert not has_hipaa, "HIPAA context should NOT be injected for Biostatistician"


def test_weaver_avoid_duplicate_dependencies(mock_context) -> None:
    """Test that dependency is not added twice if explicitly added."""
    weaver = Weaver()
    weaver.add(HIPAA_Context, context=mock_context)
    weaver.add(MedicalDirector, context=mock_context)  # Should verify HIPAA is there, but not add a second copy

    hipaa_count = sum(1 for c in weaver.components if c.name == "HIPAA")
    assert hipaa_count == 1, "HIPAA context should appear only once"


from coreason_identity.models import UserContext

def test_weaver_missing_dependency_warning(capsys: CaptureFixture[Any], mock_context: UserContext) -> None:
    """Test that a missing dependency logs a warning but doesn't crash."""
    import sys

    from loguru import logger

    # Temporarily modify MedicalDirector to have a bad dependency
    original_deps = MedicalDirector.dependencies
    MedicalDirector.dependencies = ["NonExistentContext"]

    # Loguru writes to stderr by default configuration in utils/logger.py
    # But capsys captures stdout/stderr.
    # However, loguru configuration might need to be tweaked to ensure it writes to the stderr captured by capsys.
    # The default logger setup in utils/logger.py uses `sys.stderr`.
    # When pytest runs, it replaces sys.stderr.
    # If logger was initialized BEFORE pytest replaced sys.stderr, it might be writing to the original stderr.
    # But logger.add(sys.stderr) usually picks up the current one.

    # Let's try forcing a sink for testing
    handler_id = logger.add(sys.stderr, level="WARNING")

    weaver = Weaver()
    weaver.add(MedicalDirector, context=mock_context)

    # Restore
    MedicalDirector.dependencies = original_deps
    logger.remove(handler_id)

    captured = capsys.readouterr()
    # Check stderr for the warning
    assert (
        "Dependency 'NonExistentContext' required by 'MedicalDirector' not found or could not be instantiated."
        in captured.err
    )
