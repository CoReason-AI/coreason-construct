from typing import List

from pydantic import BaseModel

from coreason_construct.schemas.base import ComponentType, PromptComponent


class RoleDefinition(BaseModel):
    """
    Defines the identity, behavior, and constraints of a specific persona.
    """

    title: str
    tone: str
    competencies: List[str]
    biases: List[str]

    def to_component(self) -> PromptComponent:
        """
        Converts the role definition into a standardized PromptComponent.
        """
        content_parts = [
            f"ROLE: {self.title}",
            f"TONE: {self.tone}",
            "COMPETENCIES:",
            "\n".join([f"- {c}" for c in self.competencies]),
            "BIASES/CONSTRAINTS:",
            "\n".join([f"- {b}" for b in self.biases]),
        ]
        return PromptComponent(
            name=self.title.replace(" ", ""),
            type=ComponentType.ROLE,
            content="\n".join(content_parts),
            priority=10,  # Roles are usually critical to identity
        )
