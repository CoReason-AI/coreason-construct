from fastapi.testclient import TestClient
from coreason_construct.server import app

client = TestClient(app)

def test_compile_empty_components() -> None:
    """Test compiling with no components (just user input)."""
    payload = {
        "user_input": "Just this.",
        "variables": {},
        "components": [],
        "max_tokens": 100
    }
    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    # System prompt might be empty or just newlines depending on weaver
    assert "Just this." in data["system_prompt"] or "Just this." in payload["user_input"]
    # The weaver puts user_input in user_message, but the endpoint returns system_prompt from config.system_message.
    # Wait, the Weaver builds system_message from components. If no components, system_message is likely empty.
    # The endpoint returns `system_prompt=config.system_message`.
    # Let's check the Weaver logic again.
    # weaver.build returns PromptConfiguration(system_message=..., user_message=...)
    # The endpoint returns CompilationResponse(system_prompt=config.system_message)
    # So if components are empty, system_prompt should be empty string.
    assert data["system_prompt"] == ""
    assert data["token_count"] == 0

def test_compile_unicode_and_emoji() -> None:
    """Test handling of unicode and emojis."""
    components = [
        {
            "name": "EmojiRole",
            "type": "ROLE",
            "content": "You are a 🤖.",
            "priority": 10
        }
    ]
    payload = {
        "user_input": "Hello 🌍!",
        "variables": {},
        "components": components
    }
    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "🤖" in data["system_prompt"]
    assert data["token_count"] > 0

def test_optimize_unicode_truncation() -> None:
    """Test optimizing text with multi-byte characters."""
    text = "🌟" * 20 # 20 emojis
    # Emojis can be multiple tokens. 🌟 is likely 1 or 2 tokens in cl100k_base.
    # Let's try to cut it in half.
    limit = 5
    payload = {
        "text": text,
        "limit": limit,
        "strategy": "prune_middle"
    }
    response = client.post("/v1/optimize", json=payload)
    assert response.status_code == 200
    opt_text = response.json()["text"]
    assert "🌟" in opt_text
    assert len(opt_text) < len(text)

def test_extreme_token_limit_compile() -> None:
    """Test compiling with extremely small token limit."""
    components = [
        {
            "name": "LongContext",
            "type": "CONTEXT",
            "content": "A" * 100,
            "priority": 1
        }
    ]
    payload = {
        "user_input": "Input",
        "components": components,
        "max_tokens": 1
    }
    response = client.post("/v1/compile", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should have dropped the context
    assert "A" * 100 not in data["system_prompt"]

def test_complex_chat_simulation_workflow() -> None:
    """
    Simulate a workflow:
    1. Initial Compile.
    2. Simulated 'Chat History' accumulates.
    3. Optimize History.
    4. Re-compile with optimized history.
    """
    # 1. Initial Compile
    role = {
        "name": "Assistant",
        "type": "ROLE",
        "content": "You are helpful.",
        "priority": 10
    }

    # 2. Simulate History Accumulation
    history_text = "User: Hi\nAssistant: Hello\n" * 50 # Long history

    # 3. Optimize History
    opt_payload = {
        "text": history_text,
        "limit": 20, # Crunch it down
        "strategy": "prune_middle"
    }
    opt_response = client.post("/v1/optimize", json=opt_payload)
    assert opt_response.status_code == 200
    optimized_history = opt_response.json()["text"]

    # 4. Re-compile with optimized history as context
    context = {
        "name": "History",
        "type": "CONTEXT",
        "content": f"History:\n{optimized_history}",
        "priority": 5
    }

    compile_payload = {
        "user_input": "New question",
        "components": [role, context],
        "max_tokens": 1000
    }

    compile_response = client.post("/v1/compile", json=compile_payload)
    assert compile_response.status_code == 200
    data = compile_response.json()

    assert "You are helpful" in data["system_prompt"]
    assert "History:" in data["system_prompt"]
    # Check that we didn't inject the full massive history
    assert len(data["system_prompt"]) < len(history_text)

def test_redundant_calls_stress_test() -> None:
    """Redundant workflow: repeatedly call endpoints."""
    text = "Repeat " * 10
    for _ in range(50):
        response = client.post("/v1/optimize", json={
            "text": text,
            "limit": 5,
            "strategy": "prune_middle"
        })
        assert response.status_code == 200
