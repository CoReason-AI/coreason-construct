# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.schemas.base import ComponentType, PromptComponent


def create_static_context(name: str, content: str, priority: int = 5) -> PromptComponent:
    """Helper to create static context components."""
    return PromptComponent(name=name, type=ComponentType.CONTEXT, content=content, priority=priority)


HIPAA_Context = create_static_context(
    name="HIPAA",
    content=(
        "You must strictly adhere to HIPAA regulations. "
        "Do not disclose Protected Health Information (PHI) unless explicitly authorized. "
        "De-identify all patient data where possible."
    ),
    priority=10,
)

GxP_Context = create_static_context(
    name="GxP",
    content=(
        "Follow GxP guidelines (Good Clinical Practice, Good Laboratory Practice, etc.). "
        "Ensure data integrity, traceability, and accountability in all responses."
    ),
    priority=9,
)
