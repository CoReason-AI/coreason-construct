# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.contexts.library import GxP_Context, HIPAA_Context
from coreason_construct.schemas.base import ComponentType


def test_hipaa_context() -> None:
    """Test HIPAA context definition."""
    context = HIPAA_Context
    assert context.name == "HIPAA"
    assert context.type == ComponentType.CONTEXT
    assert context.priority == 10
    assert "HIPAA regulations" in context.content


def test_gxp_context() -> None:
    """Test GxP context definition."""
    context = GxP_Context
    assert context.name == "GxP"
    assert context.type == ComponentType.CONTEXT
    assert context.priority == 9
    assert "GxP guidelines" in context.content
