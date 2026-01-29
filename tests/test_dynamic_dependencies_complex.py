# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from typing import Any, Generator, List, Optional

import pytest
from loguru import logger

from coreason_construct.contexts.registry import CONTEXT_REGISTRY
from coreason_construct.schemas.base import ComponentType, PromptComponent
from coreason_construct.weaver import Weaver


# --- Helpers for Dynamic Classes ---
class BaseDynamicComp(PromptComponent):
    type: ComponentType = ComponentType.CONTEXT
    dependencies: List[str] = []  # Defined as a Pydantic field

    def __init__(self, name_suffix: str, content_val: str, deps: Optional[List[str]] = None, **kwargs: Any):
        if deps is None:
            deps = []
        # We must call super().__init__ with Pydantic fields
        super().__init__(
            name=f"{self.__class__.__name__}_{name_suffix}",
            type=ComponentType.CONTEXT,
            content=f"Content: {content_val}",
            priority=5,
            dependencies=deps,
        )


class ChainC(BaseDynamicComp):
    def __init__(self, val_c: str, **kwargs: Any):
        super().__init__(name_suffix=val_c, content_val=f"C={val_c}")


class ChainB(BaseDynamicComp):
    def __init__(self, val_b: str, **kwargs: Any):
        super().__init__(name_suffix=val_b, content_val=f"B={val_b}", deps=["ChainC"])


class ChainA(BaseDynamicComp):
    def __init__(self, val_a: str, **kwargs: Any):
        super().__init__(name_suffix=val_a, content_val=f"A={val_a}", deps=["ChainB"])


class CycleA(BaseDynamicComp):
    def __init__(self, val: str, **kwargs: Any):
        super().__init__(name_suffix=val, content_val=f"CycleA={val}", deps=["CycleB"])


class CycleB(BaseDynamicComp):
    def __init__(self, val: str, **kwargs: Any):
        super().__init__(name_suffix=val, content_val=f"CycleB={val}", deps=["CycleA"])


class StrictArgsComp(BaseDynamicComp):
    def __init__(self, exact_arg: str):  # No **kwargs
        super().__init__(name_suffix=exact_arg, content_val=f"Strict={exact_arg}")


class TypeCheckComp(BaseDynamicComp):
    # This component uses Pydantic validation via the field definition if we set it,
    # but here we are testing __init__ argument passing.
    def __init__(self, count: int, **kwargs: Any):
        super().__init__(name_suffix=str(count), content_val=f"Count={count}")
        if not isinstance(count, int):
            # Just to verify what we received
            self.content += f" (Type: {type(count).__name__})"


from coreason_identity.models import UserContext


@pytest.fixture
def registry_cleanup() -> Generator[None, None, None]:
    """Saves and restores the registry state."""
    original_keys = list(CONTEXT_REGISTRY.keys())
    yield
    # Remove any keys added during tests
    current_keys = list(CONTEXT_REGISTRY.keys())
    for key in current_keys:
        if key not in original_keys:
            del CONTEXT_REGISTRY[key]


from coreason_identity.models import UserContext

def test_transitive_dynamic_chain(registry_cleanup: Any, mock_context: UserContext) -> None:
    """
    Test chain: A -> B(needs val_b) -> C(needs val_c).
    """
    CONTEXT_REGISTRY["ChainA"] = ChainA
    CONTEXT_REGISTRY["ChainB"] = ChainB
    CONTEXT_REGISTRY["ChainC"] = ChainC

    weaver = Weaver(context_data={"val_a": "1", "val_b": "2", "val_c": "3"})

    # Instantiate A manually
    root = ChainA(val_a="1")
    weaver.add(root, context=mock_context)

    # Check presence
    names = [c.name for c in weaver.components]
    assert "ChainA_1" in names
    assert "ChainB_2" in names
    assert "ChainC_3" in names


def test_partial_chain_failure(registry_cleanup: Any, capsys: Any, mock_context: UserContext) -> None:
    """
    Test chain: A -> B(needs val_b) -> C(needs val_c).
    Missing val_c. C should fail. A and B should succeed.
    """
    import sys

    # Reconfigure logger to ensure we catch the output
    # Note: Weaver uses loguru directly

    # We need to make sure loguru writes to stderr so capsys captures it
    handler_id = logger.add(sys.stderr, level="WARNING")

    CONTEXT_REGISTRY["ChainA"] = ChainA
    CONTEXT_REGISTRY["ChainB"] = ChainB
    CONTEXT_REGISTRY["ChainC"] = ChainC

    # Missing val_c
    weaver = Weaver(context_data={"val_a": "1", "val_b": "2"})

    root = ChainA(val_a="1")
    weaver.add(root, context=mock_context)

    logger.remove(handler_id)

    names = [c.name for c in weaver.components]
    assert "ChainA_1" in names
    assert "ChainB_2" in names
    assert "ChainC_3" not in names

    # Verify warning
    captured = capsys.readouterr()
    assert "Cannot instantiate dependency 'ChainC': Missing required context data: ['val_c']" in captured.err


def test_circular_dependency_dynamic(registry_cleanup: Any, mock_context: UserContext) -> None:
    """
    Test CycleA -> CycleB -> CycleA.
    """
    CONTEXT_REGISTRY["CycleA"] = CycleA
    CONTEXT_REGISTRY["CycleB"] = CycleB

    weaver = Weaver(context_data={"val": "cyc"})

    root = CycleA(val="cyc")
    weaver.add(root, context=mock_context)

    names = sorted([c.name for c in weaver.components])
    assert names == ["CycleA_cyc", "CycleB_cyc"]
    # If logic was broken, it might recurse infinitely or duplicate entries


def test_argument_filtration(registry_cleanup: Any, mock_context: UserContext) -> None:
    """
    Test that extra keys in context_data are not passed to __init__
    if it doesn't accept **kwargs.
    """
    CONTEXT_REGISTRY["StrictArgsComp"] = StrictArgsComp

    # 'garbage' should be filtered out
    weaver = Weaver(context_data={"exact_arg": "ok", "garbage": "fail"})

    # We need a component that depends on StrictArgsComp
    class DepOnStrict(BaseDynamicComp):
        def __init__(self, **kwargs: Any):
            super().__init__(name_suffix="root", content_val="root", deps=["StrictArgsComp"])

    root = DepOnStrict()
    weaver.add(root, context=mock_context)

    names = [c.name for c in weaver.components]
    assert "StrictArgsComp_ok" in names


def test_type_handling(registry_cleanup: Any, mock_context: UserContext) -> None:
    """
    Test passing string to int argument.
    """
    CONTEXT_REGISTRY["TypeCheckComp"] = TypeCheckComp

    # Pass string "5" where int is hinted
    weaver = Weaver(context_data={"count": "5"})

    class DepOnType(BaseDynamicComp):
        def __init__(self, **kwargs: Any):
            super().__init__(name_suffix="root", content_val="root", deps=["TypeCheckComp"])

    root = DepOnType()
    weaver.add(root, context=mock_context)

    comp = next(c for c in weaver.components if c.name == "TypeCheckComp_5")
    # Verify what type it received
    # Since Weaver just passes the value from dict, it should be str
    assert "Type: str" in comp.content
