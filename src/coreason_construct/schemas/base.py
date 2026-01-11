from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    ROLE = "ROLE"
    CONTEXT = "CONTEXT"
    MODE = "MODE"
    DATA = "DATA"
    PRIMITIVE = "PRIMITIVE"


class PromptComponent(BaseModel):
    name: str
    type: ComponentType
    content: str
    priority: int = Field(default=1, ge=1, le=10, description="Priority from 1 (Low) to 10 (Critical)")

    def render(self, **kwargs: Any) -> str:
        return self.content.format(**kwargs)


class PromptConfiguration(BaseModel):
    system_message: str
    user_message: str
    response_model: Optional[Type[BaseModel]]
    max_retries: int = Field(default=3, ge=0)
    provenance_metadata: Dict[str, str]  # For Veritas Logging
