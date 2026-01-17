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
from typing import Any, Dict, Optional, Type

from jinja2 import StrictUndefined, Template
from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    """
    Enum defining the types of components in the assembly line.
    """

    ROLE = "ROLE"
    CONTEXT = "CONTEXT"
    MODE = "MODE"
    DATA = "DATA"
    PRIMITIVE = "PRIMITIVE"


class PromptComponent(BaseModel):
    """
    Base class for all cognitive components.

    Attributes:
        name: Unique identifier for the component.
        type: The category of the component (Role, Context, etc.).
        content: The actual string template or content.
        priority: Importance level (1-10), where 10 is critical.
    """

    name: str
    type: ComponentType
    content: str
    priority: int = Field(default=1, ge=1, le=10)

    def render(self, **kwargs: Any) -> str:
        """
        Renders the content string with provided variables using Jinja2.

        Args:
            **kwargs: Variables to inject into the content string.

        Returns:
            The formatted string.
        """
        # Best Practice: Use Jinja2 for robust template rendering instead of str.format.
        # StrictUndefined ensures an error is raised if a variable is missing, matching the strictness of str.format.
        # We explicitly pass `undefined=StrictUndefined` to the Template constructor logic,
        # but Jinja2 Template API sets environment options slightly differently.
        # The easiest way for a single template is to pass the environment options to the constructor.
        # Note: Template(str) creates a default environment. We need to force StrictUndefined.
        # A cleaner way is to create an Environment, but for atomic rendering:
        template = Template(self.content, undefined=StrictUndefined)
        return template.render(**kwargs)


class PromptConfiguration(BaseModel):
    """
    The final output configuration for the LLM request.

    Attributes:
        system_message: The constructed system prompt.
        user_message: The final user input/task.
        response_model: The Pydantic model enforcing the output structure.
        max_retries: Number of allowed retries for the LLM call.
        provenance_metadata: Traceability data (which components created this).
    """

    system_message: str
    user_message: str
    response_model: Optional[Type[BaseModel]]
    max_retries: int = Field(default=3, ge=0)
    provenance_metadata: Dict[str, str]
