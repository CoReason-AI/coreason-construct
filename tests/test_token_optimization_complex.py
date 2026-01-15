from coreason_construct.schemas.base import ComponentType, PromptComponent
from coreason_construct.weaver import Weaver


class TestWeaverComplexScenarios:
    def test_huge_user_input_exceeds_limit(self) -> None:
        """
        Scenario: User input itself is larger than max_tokens.
        Expectation: All non-critical components are removed.
                     The final prompt exceeds max_tokens (graceful degradation), warning logged.
        """
        weaver = Weaver()
        # Add a removable component
        c1 = PromptComponent(name="Context", type=ComponentType.CONTEXT, content="Helpful info", priority=5)
        weaver.add(c1)

        # User input is ~25 tokens (100 chars). Limit is 10.
        huge_input = "A" * 100

        config = weaver.build(user_input=huge_input, max_tokens=10)

        # Context should be gone
        assert "Helpful info" not in config.system_message
        # User input remains
        assert huge_input in config.user_message

    def test_equal_priority_removal_order(self) -> None:
        """
        Scenario: Multiple components have same priority (e.g. 1).
        Expectation: Removal should be stable (likely insertion order).
        """
        weaver = Weaver()
        c1 = PromptComponent(name="First", type=ComponentType.CONTEXT, content="AAA", priority=1)
        c2 = PromptComponent(name="Second", type=ComponentType.CONTEXT, content="BBB", priority=1)

        weaver.add(c1)
        weaver.add(c2)

        # Both are small (~1 token).
        # Total with user input "I" is small.
        # Force removal of one by setting limit very tight.
        # "AAA" + "BBB" + "I" = 7 chars -> ~1 token.
        # This is tricky with integer division.
        # Let's make them bigger.
        c1.content = "A" * 20  # 5 tokens
        c2.content = "B" * 20  # 5 tokens

        # Total ~10 tokens. Limit 8. Should remove one.
        config = weaver.build(user_input="I", max_tokens=8)

        # Which one is removed?
        # Code: candidates = sorted(..., key=lambda c: c.priority).
        # Stable sort on equal keys preserves original order.
        # Original order: [First, Second].
        # Candidate 0 is First.
        # So First should be removed. Second remains.

        assert "A" * 20 not in config.system_message
        assert "B" * 20 in config.system_message

    def test_rendered_content_size_impact(self) -> None:
        """
        Scenario: Component content is small, but variable expansion is huge.
        Expectation: Token estimation accounts for expanded size, triggering removal.
        """
        weaver = Weaver()
        c1 = PromptComponent(name="VarComp", type=ComponentType.CONTEXT, content="{huge_data}", priority=5)
        weaver.add(c1)

        huge_data = "X" * 100  # 25 tokens

        # If not expanded: "{huge_data}" is ~11 chars -> 2 tokens.
        # If expanded: 100 chars -> 25 tokens.

        # Limit 10.
        # If we didn't count expansion, it would fit (2 < 10).
        # Since we count expansion, it exceeds (25 > 10). Should be removed.

        config = weaver.build(user_input="In", variables={"huge_data": huge_data}, max_tokens=10)

        assert "X" * 100 not in config.system_message

    def test_dependency_disconnect_behavior(self) -> None:
        """
        Scenario: High Priority component depends on Low Priority component.
        Expectation: Low Priority component is removed, High Priority remains.
        (Verifying current behavior, even if suboptimal for logic).
        """
        weaver = Weaver()

        # Role (P8) depends on Context (P2)
        role = PromptComponent(
            name="MyRole",
            type=ComponentType.ROLE,
            content="I am a Role.",
            priority=8,
            # dependencies=["MyContext"] # dependency logic is in add()
        )
        context = PromptComponent(
            name="MyContext", type=ComponentType.CONTEXT, content="I am critical context.", priority=2
        )

        # Add manually to simulate resolved dependencies
        weaver.add(context)
        weaver.add(role)

        # Both added.
        # Total size small.
        # Set limit to force removal of Context (P2) but keep Role (P8).
        # "I am a Role." (12) + "I am critical context." (22) + "In" (2) = ~36 chars -> 9 tokens.
        # Limit 6.
        # Should remove Context (P2). Role (P8) stays.

        config = weaver.build(user_input="In", max_tokens=6)

        assert "I am critical context" not in config.system_message
        assert "I am a Role" in config.system_message

    def test_zero_max_tokens(self) -> None:
        """
        Scenario: max_tokens is 0.
        Expectation: Remove everything except Critical (P10).
        """
        weaver = Weaver()
        c1 = PromptComponent(name="C1", type=ComponentType.CONTEXT, content="Info", priority=5)
        weaver.add(c1)

        config = weaver.build(user_input="Input", max_tokens=0)

        assert "Info" not in config.system_message
