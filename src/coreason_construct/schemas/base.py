from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel


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
    priority: int = 1  # 1 (Low) to 10 (Critical)

    def render(self, **kwargs: Any) -> str:
        return self.content.format(**kwargs)


class PromptConfiguration(BaseModel):
    system_message: str
    user_message: str
    response_model: Optional[Type[BaseModel]]
    max_retries: int = 3
    provenance_metadata: Dict[str, str]  # For Veritas Logging
