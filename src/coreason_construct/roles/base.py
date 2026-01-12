from typing import List

from pydantic import BaseModel, Field, field_validator

from coreason_construct.schemas.base import ComponentType, PromptComponent


class RoleDefinition(BaseModel):
    """
    Defines the identity, behavior, and constraints of a specific persona.
    """

    title: str = Field(..., min_length=1, description="The specific name of the role (e.g. 'Medical Director')")
    tone: str = Field(..., min_length=1, description="The persona's voice and attitude")
    competencies: List[str] = Field(default_factory=list)
    biases: List[str] = Field(default_factory=list)

    @field_validator("title", "tone")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Ensures strings are not empty or just whitespace."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace only")
        return cleaned

    def to_component(self) -> PromptComponent:
        """
        Converts the role definition into a standardized PromptComponent.
        """
        content_parts = [
            f"ROLE: {self.title}",
            f"TONE: {self.tone}",
        ]

        if self.competencies:
            content_parts.append("COMPETENCIES:")
            # Handle multi-line competencies or bullets safely
            for c in self.competencies:
                # Ensure we don't double-bullet if the user added one
                clean_c = c.lstrip("- ").strip()
                content_parts.append(f"- {clean_c}")

        if self.biases:
            content_parts.append("BIASES/CONSTRAINTS:")
            for b in self.biases:
                clean_b = b.lstrip("- ").strip()
                content_parts.append(f"- {clean_b}")

        return PromptComponent(
            # Sanitize name for ID usage (remove special chars, keep alphanumeric)
            name="".join(x for x in self.title if x.isalnum()),
            type=ComponentType.ROLE,
            content="\n".join(content_parts),
            priority=10,  # Roles are usually critical to identity
        )
