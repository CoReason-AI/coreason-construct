# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_identity.models import UserContext

from coreason_construct.data.library import AE_Examples
from coreason_construct.roles.library import SafetyScientist
from coreason_construct.schemas.base import ComponentType, PromptComponent
from coreason_construct.weaver import Weaver


def test_weaver_integration_ae_examples(mock_context: UserContext) -> None:
    """
    Test full assembly with SafetyScientist and AE_Examples.
    """
    weaver = Weaver()
    weaver.add(SafetyScientist, context=mock_context)
    weaver.add(AE_Examples, context=mock_context)

    config = weaver.build(user_input="Subject reported headache.", context=mock_context)
    system_msg = config.system_message

    # Check Role
    assert "Senior Safety Scientist" in system_msg
    # Check Dependency
    assert "HIPAA" in system_msg
    # Check AE_Examples
    assert "Input: Patient reported mild nausea." in system_msg
    assert "'term': 'Nausea'" in system_msg


def test_mixed_rendering_variables(mock_context: UserContext) -> None:
    """
    Test scenario where some components need variables and AE_Examples (with braces) does not.
    This ensures the render override correctly isolates AE_Examples from variable injection.
    """
    # Create a component that REQUIRES a variable
    dynamic_comp = PromptComponent(
        name="Greeter",
        type=ComponentType.CONTEXT,
        content="Hello, {{ user_name }}. Welcome to the study.",
        priority=5,
    )

    weaver = Weaver()
    weaver.add(dynamic_comp, context=mock_context)
    weaver.add(AE_Examples, context=mock_context)

    # Build with variable
    variables = {"user_name": "Dr. Alice"}
    config = weaver.build(user_input="Test input", variables=variables, context=mock_context)
    system_msg = config.system_message

    # Verify dynamic component rendered correctly
    assert "Hello, Dr. Alice." in system_msg

    # Verify AE_Examples rendered correctly (and didn't crash on braces)
    assert "Input: Patient reported mild nausea." in system_msg
    assert "'severity': 'FATAL'" in system_msg
