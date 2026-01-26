from fastapi.testclient import TestClient
from coreason_construct.server import app

client = TestClient(app)

def test_compile_endpoint() -> None:
    components = [
        {
            "name": "TestRole",
            "type": "ROLE",
            "content": "You are a helpful assistant.",
            "priority": 10
        },
        {
            "name": "TestContext",
            "type": "CONTEXT",
            "content": "Use simple language.",
            "priority": 5
        }
    ]

    payload = {
        "user_input": "Explain quantum physics.",
        "variables": {},
        "components": components,
        "max_tokens": 1000
    }

    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "system_prompt" in data
    assert "token_count" in data
    assert data["token_count"] > 0
    assert "You are a helpful assistant" in data["system_prompt"]
    assert "Use simple language" in data["system_prompt"]

def test_compile_token_limit_exceeded() -> None:
    # Test that components are dropped if limit is low
    components = [
        {
            "name": "Critical",
            "type": "ROLE",
            "content": "Critical " * 10,
            "priority": 10
        },
        {
            "name": "Optional",
            "type": "CONTEXT",
            "content": "Optional " * 10,
            "priority": 1
        }
    ]

    # "Critical " * 10 ~ 10-20 tokens?
    # "Optional " * 10 ~ 10-20 tokens?
    # Total ~ 30-40.
    # Limit 15.

    payload = {
        "user_input": "Input",
        "variables": {},
        "components": components,
        "max_tokens": 15
    }

    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Critical" in data["system_prompt"]
    assert "Optional" not in data["system_prompt"]

def test_optimize_endpoint() -> None:
    # "Hello " is 1 token in cl100k_base.
    text = "Hello " * 20 # 20 tokens
    limit = 5

    payload = {
        "text": text,
        "limit": limit,
        "strategy": "prune_middle"
    }

    response = client.post("/v1/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    optimized_text = data["text"]

    # Check that it was truncated
    assert len(optimized_text) < len(text)

    # Check approximate token count (should be <= limit)
    # We can't easily check exact tokens here without tiktoken, but length check confirms modification.
    assert "Hello" in optimized_text

def test_optimize_invalid_strategy() -> None:
    payload = {
        "text": "test",
        "limit": 10,
        "strategy": "invalid_strategy"
    }
    response = client.post("/v1/optimize", json=payload)
    # Pydantic validation error is usually 422
    assert response.status_code == 422

def test_optimize_no_truncation_needed() -> None:
    text = "Short"
    limit = 100
    payload = {
        "text": text,
        "limit": limit,
        "strategy": "prune_middle"
    }
    response = client.post("/v1/optimize", json=payload)
    assert response.status_code == 200
    assert response.json()["text"] == text

def test_optimize_limit_zero() -> None:
    text = "Any text"
    limit = 0
    payload = {
        "text": text,
        "limit": limit,
        "strategy": "prune_middle"
    }
    response = client.post("/v1/optimize", json=payload)
    assert response.status_code == 200
    assert response.json()["text"] == ""
