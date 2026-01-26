import tiktoken
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from coreason_construct.weaver import Weaver
from coreason_construct.schemas.base import PromptComponent

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

def prune_middle(text: str, limit: int, encoding: Any) -> str:
    tokens = encoding.encode(text)
    if len(tokens) <= limit:
        return text

    # If limit is very small (e.g. 0 or 1), handle gracefully
    if limit <= 0:
        return ""

    # Calculate how many tokens to keep at start and end
    # We want start + end = limit
    # If limit is odd, start gets one more? or end?
    # limit // 2 + (limit - limit // 2) = limit.

    half_limit = limit // 2
    remainder = limit - half_limit # This handles odd limits (e.g. 5 -> 2 + 3)

    # To strictly "prune middle", we usually keep equal parts or favor start/end.
    # Let's do ceiling for start? Or floor?
    # Standard prune middle often keeps header and footer.
    # Let's do `ceil(limit/2)` for start and `floor(limit/2)` for end?
    # Or just simple split.

    start_count = (limit + 1) // 2
    end_count = limit - start_count

    start_tokens = tokens[:start_count]
    end_tokens = tokens[-end_count:] if end_count > 0 else []

    return encoding.decode(start_tokens + end_tokens)

@app.post("/v1/compile", response_model=CompilationResponse)
async def compile_blueprint(request: BlueprintRequest):
    weaver = Weaver(context_data=request.variables)

    for component in request.components:
        weaver.add(component)

    config = weaver.build(
        user_input=request.user_input,
        variables=request.variables,
        max_tokens=request.max_tokens
    )

    encoding = tiktoken.get_encoding("cl100k_base")
    token_count = len(encoding.encode(config.system_message))

    return CompilationResponse(
        system_prompt=config.system_message,
        token_count=token_count,
        warnings=[]
    )

@app.post("/v1/optimize", response_model=OptimizationResponse)
async def optimize_text(request: OptimizationRequest):
    encoding = tiktoken.get_encoding("cl100k_base")
    optimized_text = prune_middle(request.text, request.limit, encoding)

    return OptimizationResponse(text=optimized_text)
