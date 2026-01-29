from fastapi.testclient import TestClient

from coreason_construct.server import app

client = TestClient(app)


def test_compile_returns_dropped_components_as_warnings() -> None:
    # 1. Create a request with low priority components that exceed max_tokens

    # High priority: "Important" * 10 ~ 90 chars ~ 20-25 tokens. Priority 10.
    # Low priority: "Optional" * 50 ~ 400 chars ~ 100 tokens. Priority 1.
    # User Input: "Input" ~ 1 token.
    # Max tokens: 50.

    # Expected: High Priority kept. Low Priority dropped.

    payload = {
        "user_input": "Input",
        "variables": {},
        "components": [
            {"name": "HighPriority", "type": "CONTEXT", "content": "Important " * 10, "priority": 10},
            {"name": "LowPriority", "type": "CONTEXT", "content": "Optional " * 50, "priority": 1},
        ],
        "max_tokens": 50,
    }

    response = client.post("/v1/compile", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Verify warnings contain the name of the dropped component
    assert "LowPriority" in data["warnings"]
    assert "HighPriority" not in data["warnings"]

    # Verify content
    assert "Important" in data["system_prompt"]
    assert "Optional" not in data["system_prompt"]


def test_compile_no_warnings_when_limit_ok() -> None:
    payload = {
        "user_input": "Input",
        "variables": {},
        "components": [{"name": "HighPriority", "type": "CONTEXT", "content": "Important", "priority": 10}],
        "max_tokens": 1000,
    }

    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["warnings"] == []
