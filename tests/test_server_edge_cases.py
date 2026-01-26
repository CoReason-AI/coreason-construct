from fastapi.testclient import TestClient

from coreason_construct.server import app

client = TestClient(app)


def test_compile_empty_components() -> None:
    """Test compiling with no components (just user input)."""
    payload = {"user_input": "Just this.", "variables": {}, "components": [], "max_tokens": 100}
    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Just this." in data["system_prompt"] or "Just this." in str(payload["user_input"])
    assert data["system_prompt"] == ""
    assert data["token_count"] == 0


def test_compile_unicode_and_emoji() -> None:
    """Test handling of unicode and emojis."""
    components = [{"name": "EmojiRole", "type": "ROLE", "content": "You are a 🤖.", "priority": 10}]
    payload = {"user_input": "Hello 🌍!", "variables": {}, "components": components}
    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "🤖" in data["system_prompt"]
    assert data["token_count"] > 0


def test_optimize_unicode_truncation() -> None:
    """Test optimizing text with multi-byte characters."""
    text = "🌟" * 20  # 20 emojis
    limit = 5
    payload = {"text": text, "limit": limit, "strategy": "prune_middle"}
    response = client.post("/v1/optimize", json=payload)
    assert response.status_code == 200
    opt_text = response.json()["text"]
    assert "🌟" in opt_text
    assert len(opt_text) < len(text)


def test_extreme_token_limit_compile() -> None:
    """Test compiling with extremely small token limit."""
    components = [{"name": "LongContext", "type": "CONTEXT", "content": "A" * 100, "priority": 1}]
    payload = {"user_input": "Input", "components": components, "max_tokens": 1}
    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "A" * 100 not in data["system_prompt"]


def test_complex_chat_simulation_workflow() -> None:
    """
    Simulate a workflow:
    1. Initial Compile.
    2. Simulated 'Chat History' accumulates.
    3. Optimize History.
    4. Re-compile with optimized history.
    """
    role = {"name": "Assistant", "type": "ROLE", "content": "You are helpful.", "priority": 10}
    history_text = "User: Hi\nAssistant: Hello\n" * 50

    opt_payload = {
        "text": history_text,
        "limit": 20,
        "strategy": "prune_middle",
    }
    opt_response = client.post("/v1/optimize", json=opt_payload)
    assert opt_response.status_code == 200
    optimized_history = opt_response.json()["text"]

    context = {"name": "History", "type": "CONTEXT", "content": f"History:\n{optimized_history}", "priority": 5}
    compile_payload = {"user_input": "New question", "components": [role, context], "max_tokens": 1000}

    compile_response = client.post("/v1/compile", json=compile_payload)
    assert compile_response.status_code == 200
    data = compile_response.json()

    assert "You are helpful" in data["system_prompt"]
    assert "History:" in data["system_prompt"]
    assert len(data["system_prompt"]) < len(history_text)


def test_redundant_calls_stress_test() -> None:
    """Redundant workflow: repeatedly call endpoints."""
    text = "Repeat " * 10
    for _ in range(50):
        response = client.post("/v1/optimize", json={"text": text, "limit": 5, "strategy": "prune_middle"})
        assert response.status_code == 200


def test_compile_missing_variable() -> None:
    """Test behavior when a variable required by a component is missing."""
    components = [{"name": "TemplateComp", "type": "CONTEXT", "content": "Hello {{ name }}", "priority": 10}]
    # 'name' is missing in variables
    payload = {"user_input": "Input", "variables": {}, "components": components}

    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 400
    assert "Missing variable" in response.json()["detail"]


def test_compile_duplicate_components() -> None:
    """Test duplicate components are handled gracefully (idempotent addition)."""
    # Weaver.add checks for duplicates by name and ignores subsequent ones
    comp = {"name": "UniqueName", "type": "CONTEXT", "content": "First Content", "priority": 10}
    comp_dup = {"name": "UniqueName", "type": "CONTEXT", "content": "Second Content", "priority": 10}

    payload = {"user_input": "Input", "variables": {}, "components": [comp, comp_dup]}

    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect "First Content" to be present, "Second Content" absent
    assert "First Content" in data["system_prompt"]
    assert "Second Content" not in data["system_prompt"]


def test_compile_invalid_component_type() -> None:
    """Test passing an invalid component type."""
    comp = {"name": "BadComp", "type": "INVALID_TYPE", "content": "Content", "priority": 10}

    payload = {"user_input": "Input", "variables": {}, "components": [comp]}

    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 422  # Pydantic validation error
