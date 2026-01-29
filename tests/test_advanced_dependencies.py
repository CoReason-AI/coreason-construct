# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_identity.models import UserContext

from coreason_construct.contexts.registry import CONTEXT_REGISTRY
from coreason_construct.schemas.base import ComponentType, PromptComponent
from coreason_construct.weaver import Weaver


class MockComponentWithDeps(PromptComponent):
    dependencies: list[str] = []

    def __init__(self, name: str, dependencies: list[str]):
        super().__init__(name=name, type=ComponentType.CONTEXT, content=f"Content for {name}")
        self.dependencies = dependencies


def test_transitive_dependencies(mock_context: UserContext) -> None:
    """
    Test chain: RoleA -> ContextB -> ContextC
    Adding RoleA should add ContextB and ContextC.
    """
    # Create components
    context_c = MockComponentWithDeps(name="ContextC", dependencies=[])
    context_b = MockComponentWithDeps(name="ContextB", dependencies=["ContextC"])
    role_a = MockComponentWithDeps(name="RoleA", dependencies=["ContextB"])

    # Register them
    CONTEXT_REGISTRY["ContextB"] = context_b
    CONTEXT_REGISTRY["ContextC"] = context_c

    # Test
    weaver = Weaver()
    weaver.add(role_a, context=mock_context)

    component_names = {c.name for c in weaver.components}
    assert "RoleA" in component_names
    assert "ContextB" in component_names
    assert "ContextC" in component_names

    # Clean up registry
    del CONTEXT_REGISTRY["ContextB"]
    del CONTEXT_REGISTRY["ContextC"]


def test_circular_dependencies(mock_context: UserContext) -> None:
    """
    Test loop: ContextX -> ContextY -> ContextX
    Adding ContextX should add ContextY and stop without infinite loop.
    """
    # Create components
    context_x = MockComponentWithDeps(name="ContextX", dependencies=["ContextY"])
    context_y = MockComponentWithDeps(name="ContextY", dependencies=["ContextX"])

    # Register them
    CONTEXT_REGISTRY["ContextX"] = context_x
    CONTEXT_REGISTRY["ContextY"] = context_y

    # Test
    weaver = Weaver()
    weaver.add(context_x, context=mock_context)

    component_names = {c.name for c in weaver.components}
    assert "ContextX" in component_names
    assert "ContextY" in component_names
    assert len(weaver.components) == 2

    # Clean up registry
    del CONTEXT_REGISTRY["ContextX"]
    del CONTEXT_REGISTRY["ContextY"]


def test_overlapping_dependencies(mock_context: UserContext) -> None:
    """
    Test: RoleA -> [ContextShared]
          RoleB -> [ContextShared]
    Adding both should result in only one ContextShared.
    """
    # Create components
    context_shared = MockComponentWithDeps(name="ContextShared", dependencies=[])
    role_a = MockComponentWithDeps(name="RoleA", dependencies=["ContextShared"])
    role_b = MockComponentWithDeps(name="RoleB", dependencies=["ContextShared"])

    # Register
    CONTEXT_REGISTRY["ContextShared"] = context_shared

    # Test
    weaver = Weaver()
    weaver.add(role_a, context=mock_context)
    weaver.add(role_b, context=mock_context)

    component_names = {c.name for c in weaver.components}
    assert "RoleA" in component_names
    assert "RoleB" in component_names
    assert "ContextShared" in component_names

    # Count instances of ContextShared
    count = sum(1 for c in weaver.components if c.name == "ContextShared")
    assert count == 1

    # Clean up registry
    del CONTEXT_REGISTRY["ContextShared"]
