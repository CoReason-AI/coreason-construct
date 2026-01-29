# Requirements

This document lists the dependencies required to run `coreason-construct` in both Library Mode and Service Mode.

## Core Library Dependencies

These are required for using `coreason-construct` as a Python library.

*   `python >= 3.12`
*   `loguru ^0.7.2`: For structured logging.
*   `pydantic ^2.0.0`: For data validation and schema definition.
*   `instructor ^1.0.0`: For patching LLM clients to return structured data.
*   `jinja2 ^3.1.0`: For template rendering of components.
*   `coreason-identity ^0.4.1`: For identity management integration.
*   `anyio ^4.12.1`: For asynchronous support.

## Service Mode Dependencies (Microservice)

These are additional requirements for running `coreason-construct` as a standalone microservice (Service C).

*   `fastapi`: For the high-performance API server.
*   `uvicorn[standard]`: ASGI server implementation.
*   `tiktoken`: For BPE tokenization and token counting logic used in optimization.

## Development Dependencies

Required for contributing to the project.

*   `pytest`: Testing framework.
*   `ruff`: Linter and formatter.
*   `pre-commit`: Git hooks management.
*   `mkdocs` & `mkdocs-material`: Documentation generation.
*   `mypy`: Static type checking.
*   `httpx`: HTTP client for testing the API.
