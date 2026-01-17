# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.data.library import AE_Examples
from coreason_construct.primitives.extract import ExtractionPrimitive
from coreason_construct.roles.library import SafetyScientist
from coreason_construct.schemas.clinical import AdverseEvent
from coreason_construct.weaver import Weaver


def test_user_story_b_assembly() -> None:
    """
    Test the assembly for User Story B: The "Type-Safe" Extraction.
    Goal: Extract Adverse Events.
    Components:
    - Role: SafetyScientist
    - Data: FewShotBank("AE_Examples")
    - Primitive: ExtractionPrimitive(schema=AdverseEvent)
    """
    weaver = Weaver()

    # Add components
    weaver.add(SafetyScientist)
    weaver.add(AE_Examples)
    weaver.add(ExtractionPrimitive(name="AE_Extraction", schema=AdverseEvent))

    # Build prompt
    user_input = "Patient reported experiencing mild nausea after the first dose."
    config = weaver.build(user_input=user_input)

    # Verify Weaver Logic
    # 1. Dependency Resolution: SafetyScientist requires HIPAA and GxP
    assert "HIPAA" in [c.name for c in weaver.components]
    assert "GxP" in [c.name for c in weaver.components]
    assert "SafetyScientist" in [c.name for c in weaver.components]
    assert "AE_Examples" in [c.name for c in weaver.components]
    assert "AE_Extraction" in [c.name for c in weaver.components]

    # 2. Response Model
    assert config.response_model is AdverseEvent

    # 3. System Message Content
    # Should include Role content, Contexts, and Data (FewShot)
    assert "Safety Scientist" in config.system_message
    assert "HIPAA" in config.system_message
    assert "GxP" in config.system_message
    assert "Patient reported nausea" in config.system_message
    assert "Ideal Output" in config.system_message

    # 4. User Message Content
    # Should include the Primitive task and the User Input
    assert "Extract the following information" in config.user_message
    assert "AdverseEvent" in config.user_message
    assert user_input in config.user_message

    # 5. Provenance Metadata
    assert config.provenance_metadata["role"] == "SafetyScientist"
    assert config.provenance_metadata["schema"] == "AdverseEvent"
