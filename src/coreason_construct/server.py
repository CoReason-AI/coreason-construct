from typing import Any, Dict, List, Optional

import tiktoken
from fastapi import FastAPI
from pydantic import BaseModel, Field
from tiktoken import Encoding

from coreason_construct.schemas.base import PromptComponent
from coreason_construct.weaver import Weaver

app = FastAPI(title="Coreason Construct Compiler", version="1.0.0")


class BlueprintRequest(BaseModel):
    user_input: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    components: List[PromptComponent]
    max_tokens: Optional[int] = None


class OptimizationRequest(BaseModel):
    text: str
    limit: int
    strategy: str = Field(..., pattern="^prune_middle$")


class CompilationResponse(BaseModel):
    system_prompt: str
    token_count: int
    warnings: List[str] = []


class OptimizationResponse(BaseModel):
    text: str


def prune_middle(text: str, limit: int, encoding: Encoding) -> str:
    tokens = encoding.encode(text)
    if len(tokens) <= limit:
        return text

    # If limit is very small (e.g. 0 or 1), handle gracefully
    if limit <= 0:
        return ""

    # Calculate how many tokens to keep at start and end
    # We want start + end = limit

    start_count = (limit + 1) // 2
    end_count = limit - start_count

    start_tokens = tokens[:start_count]
    end_tokens = tokens[-end_count:] if end_count > 0 else []

    # Cast to str explicitly if mypy complains, but Encoding.decode usually returns str
    decoded: str = encoding.decode(start_tokens + end_tokens)
    return decoded


@app.post("/v1/compile", response_model=CompilationResponse)
async def compile_blueprint(request: BlueprintRequest) -> CompilationResponse:
    weaver = Weaver(context_data=request.variables)

    for component in request.components:
        weaver.add(component)

    config = weaver.build(user_input=request.user_input, variables=request.variables, max_tokens=request.max_tokens)

    encoding = tiktoken.get_encoding("cl100k_base")
    token_count = len(encoding.encode(config.system_message))

    return CompilationResponse(system_prompt=config.system_message, token_count=token_count, warnings=[])


@app.post("/v1/optimize", response_model=OptimizationResponse)
async def optimize_text(request: OptimizationRequest) -> OptimizationResponse:
    encoding = tiktoken.get_encoding("cl100k_base")
    optimized_text = prune_middle(request.text, request.limit, encoding)

    return OptimizationResponse(text=optimized_text)
