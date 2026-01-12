# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from enum import Enum
from typing import Dict, Optional, Type

from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    """Enumeration of component types."""

    ROLE = "ROLE"
    CONTEXT = "CONTEXT"
    MODE = "MODE"
    DATA = "DATA"
    PRIMITIVE = "PRIMITIVE"


class PromptComponent(BaseModel):
    """A component of a prompt."""

    name: str
    type: ComponentType
    content: str
    priority: int = Field(default=1, ge=1, le=10)  # 1 (Low) to 10 (Critical)

    def render(self, **kwargs: str) -> str:
        """Render the component content with the given arguments."""
        return self.content.format(**kwargs)


class PromptConfiguration(BaseModel):
    """Configuration for a prompt execution."""

    system_message: str
    user_message: str
    response_model: Optional[Type[BaseModel]]
    max_retries: int = Field(default=3, ge=0)
    provenance_metadata: Dict[str, str]  # For Veritas Logging
