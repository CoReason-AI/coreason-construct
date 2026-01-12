# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from coreason_construct.contexts.library import HIPAA_Context
from coreason_construct.primitives.base import StructuredPrimitive
from coreason_construct.schemas.base import ComponentType, PromptComponent, PromptConfiguration


class Weaver:
    """
    The Builder Engine that stitches components into the final request configuration.
    """

    def __init__(self) -> None:
        self.components: List[PromptComponent] = []
        self._response_model: Optional[Type[BaseModel]] = None

    def _has_component(self, name: str) -> bool:
        return any(c.name == name for c in self.components)

    def _sort_components(self, components: List[PromptComponent]) -> List[PromptComponent]:
        # Sort by priority (descending), then stable
        return sorted(components, key=lambda c: c.priority, reverse=True)

    def add(self, component: PromptComponent) -> "Weaver":
        """
        Add a component to the weaver.
        Handles dependency resolution.
        """
        # 1. Dependency Resolution
        if component.name == "MedicalDirector" and not self._has_component("HIPAA"):
            self.components.append(HIPAA_Context)

        self.components.append(component)

        if isinstance(component, StructuredPrimitive):
            self._response_model = component.response_model

        return self

    def build(self, user_input: str, variables: Optional[Dict[str, Any]] = None) -> PromptConfiguration:
        """
        Build the final prompt configuration.
        """
        if variables is None:
            variables = {}
        # 2. Optimization (Mock logic)
        # if total_tokens > limit: remove_low_priority(self.components)

        sorted_comps = self._sort_components(self.components)

        system_parts = [c.render(**variables) for c in sorted_comps if c.type != ComponentType.PRIMITIVE]

        # Primitive's content (task instructions) usually goes at the end or in user message,
        # but PRD says "task_part = next(...)" so we treat it specifically.
        task_part = next((c.render(**variables) for c in sorted_comps if c.type == ComponentType.PRIMITIVE), "")

        final_user_msg = f"{task_part}\n\nINPUT DATA:\n{user_input}" if task_part else user_input

        # 3. Provenance Capture
        metadata = {
            "role": next((c.name for c in self.components if c.type == ComponentType.ROLE), "None"),
            "mode": next((c.name for c in self.components if c.type == ComponentType.MODE), "None"),
            "schema": self._response_model.__name__ if self._response_model else "None",
        }

        return PromptConfiguration(
            system_message="\n\n".join(system_parts),
            user_message=final_user_msg,
            response_model=self._response_model,
            provenance_metadata=metadata,
        )
