from coreason_construct.schemas.base import ComponentType, PromptComponent
from coreason_construct.weaver import Weaver


class TestWeaverTokenOptimization:
    def test_token_optimization_no_truncation_needed(self) -> None:
        """Test that no components are removed if token count is within limit."""
        weaver = Weaver()

        # Add high priority component
        high_p = PromptComponent(name="HighPriority", type=ComponentType.CONTEXT, content="Critical " * 10, priority=10)
        weaver.add(high_p)

        # Add low priority component
        low_p = PromptComponent(name="LowPriority", type=ComponentType.CONTEXT, content="Optional " * 10, priority=1)
        weaver.add(low_p)

        # Build with generous limit (assuming 4 chars/token approx)
        # Content length approx 90 + 90 = 180 chars -> ~45 tokens.
        # User input ~ 10 chars -> 3 tokens.
        # Total ~ 50 tokens. Limit 100.
        config = weaver.build(user_input="Test input", max_tokens=100)

        # Check system message content instead of metadata for generic Contexts
        assert "Critical" in config.system_message
        assert "Optional" in config.system_message

    def test_token_optimization_truncates_low_priority(self) -> None:
        """Test that low priority components are removed when limit is exceeded."""
        weaver = Weaver()

        # High priority: ~40 chars -> 10 tokens
        high_p = PromptComponent(name="HighPriority", type=ComponentType.CONTEXT, content="Important " * 4, priority=10)
        weaver.add(high_p)

        # Low priority: ~400 chars -> 100 tokens
        low_p = PromptComponent(name="LowPriority", type=ComponentType.CONTEXT, content="Optional " * 50, priority=1)
        weaver.add(low_p)

        # User input: "Input" -> ~2 tokens
        # Total needed: ~112 tokens.
        # Set limit to 50 tokens. Should drop LowPriority.

        config = weaver.build(user_input="Input", max_tokens=50)

        assert "Important" in config.system_message
        assert "Optional" not in config.system_message

    def test_token_optimization_preserves_higher_priority(self) -> None:
        """Test that among multiple components, lowest priority goes first."""
        weaver = Weaver()

        c1 = PromptComponent(name="P1", type=ComponentType.CONTEXT, content="A" * 40, priority=1)  # ~10 tokens
        c5 = PromptComponent(name="P5", type=ComponentType.CONTEXT, content="B" * 40, priority=5)  # ~10 tokens
        c9 = PromptComponent(name="P9", type=ComponentType.CONTEXT, content="C" * 40, priority=9)  # ~10 tokens

        weaver.add(c1).add(c5).add(c9)

        # Total ~30 tokens + user input.
        # Limit 25 tokens. Should drop P1.
        config = weaver.build(user_input="In", max_tokens=25)
        assert "A" * 40 not in config.system_message
        assert "B" * 40 in config.system_message
        assert "C" * 40 in config.system_message

        # Limit 15 tokens. Should drop P1 and P5.
        config = weaver.build(user_input="In", max_tokens=15)
        assert "A" * 40 not in config.system_message
        assert "B" * 40 not in config.system_message
        assert "C" * 40 in config.system_message

    def test_token_optimization_preserves_primitives(self) -> None:
        """Test that Primitive tasks (which are critical) are treated carefully or preserved."""
        # Primitives usually have priority 10 by default in library.
        # But let's check explicit behavior.

        from pydantic import BaseModel

        from coreason_construct.primitives.base import StructuredPrimitive

        class MockModel(BaseModel):
            pass

        prim = StructuredPrimitive(name="Task", content="Do X " * 10, response_model=MockModel, priority=10)
        weaver = Weaver()
        weaver.add(prim)

        # Even with tight limit, priority 10 should stay if possible.
        # If limit is impossibly small, we might still return it or fail.
        # Current logic is "remove lowest priority". If all are 10, maybe it removes nothing or arbitrary?
        # Ideally it shouldn't remove the Task.

        config = weaver.build(user_input="In", max_tokens=5)
        # 5 tokens is very small (~20 chars). Primitive content is "Do X " * 10 ~ 50 chars.
        # Logic: If all components are retained (can't remove Priority 10?), it will just exceed limit.
        # Or if it removes Priority 10? PRD says "truncate Low Priority".
        # We'll assume priority 10 is 'safe' from truncation unless we implement specific logic.
        # But the naive loop might remove P10 if it's the 'lowest' available (i.e. all are P10).
        # Let's see what happens.

        assert "Do X" in config.user_message  # Primitives go to user message in build()

    def test_token_optimization_stop_truncation_at_critical(self) -> None:
        """Test that truncation stops when only critical components remain, even if over limit."""
        weaver = Weaver()

        # Two Critical components
        c1 = PromptComponent(name="C1", type=ComponentType.CONTEXT, content="Critical1 " * 10, priority=10)
        c2 = PromptComponent(name="C2", type=ComponentType.CONTEXT, content="Critical2 " * 10, priority=10)

        weaver.add(c1).add(c2)

        # Total size is large. Limit is small.
        # Should not remove either because both are P10.
        config = weaver.build(user_input="In", max_tokens=10)

        assert "Critical1" in config.system_message
        assert "Critical2" in config.system_message

    def test_token_optimization_removes_all_non_critical(self) -> None:
        """Test that all non-critical components are removed if necessary."""
        weaver = Weaver()
        c1 = PromptComponent(name="C1", type=ComponentType.CONTEXT, content="Low " * 10, priority=1)
        weaver.add(c1)

        # User input small. Limit small (but big enough for user input).
        # "Low " * 10 = 40 chars -> 10 tokens.
        # User input "A" -> 0 tokens (len 1).
        # Limit 5.
        config = weaver.build(user_input="A", max_tokens=5)

        assert "Low" not in config.system_message
        # This should trigger line 193 if we remove C1 and active_components becomes empty.
