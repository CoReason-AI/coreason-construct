# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.modes.hats import SixThinkingHats
from coreason_construct.modes.reasoning import ReasoningPatterns
from coreason_construct.schemas.base import ComponentType


def test_six_hats() -> None:
    """Test Six Thinking Hats components."""
    hats = [
        (SixThinkingHats.White, "White", "Facts"),
        (SixThinkingHats.Red, "Red", "Emotions"),
        (SixThinkingHats.Black, "Black", "Caution"),
        (SixThinkingHats.Yellow, "Yellow", "Optimism"),
        (SixThinkingHats.Green, "Green", "Creativity"),
        (SixThinkingHats.Blue, "Blue", "Process control"),
    ]

    for hat, color, keyword in hats:
        assert hat.type == ComponentType.MODE
        assert hat.name == f"SixHats_{color}"
        assert color in hat.content
        assert keyword in hat.content


def test_reasoning_patterns() -> None:
    """Test Reasoning Patterns components."""
    assert ReasoningPatterns.FirstPrinciples.name == "Reasoning_FirstPrinciples"
    assert "First Principles" in ReasoningPatterns.FirstPrinciples.content

    assert ReasoningPatterns.PreMortem.name == "Reasoning_PreMortem"
    assert "Pre-Mortem" in ReasoningPatterns.PreMortem.content

    assert ReasoningPatterns.ChainOfVerification.name == "Reasoning_ChainOfVerification"
    assert "Chain of Verification" in ReasoningPatterns.ChainOfVerification.content
