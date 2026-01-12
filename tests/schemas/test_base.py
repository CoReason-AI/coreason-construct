# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

import pytest
from pydantic import BaseModel, ValidationError

from coreason_construct.schemas.base import ComponentType, PromptComponent, PromptConfiguration


def test_component_type_enum() -> None:
    """Test ComponentType enum values."""
    assert ComponentType.ROLE == "ROLE"
    assert ComponentType.CONTEXT == "CONTEXT"
    assert ComponentType.MODE == "MODE"
    assert ComponentType.DATA == "DATA"
    assert ComponentType.PRIMITIVE == "PRIMITIVE"


def test_prompt_component_initialization() -> None:
    """Test PromptComponent initialization with valid data."""
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="You are a {role}.", priority=5)
    assert component.name == "TestRole"
    assert component.type == ComponentType.ROLE
    assert component.content == "You are a {role}."
    assert component.priority == 5


def test_prompt_component_priority_validation() -> None:
    """Test PromptComponent priority validation (1-10)."""
    # Test lower bound violation
    with pytest.raises(ValidationError):
        PromptComponent(name="TestRole", type=ComponentType.ROLE, content="test", priority=0)

    # Test upper bound violation
    with pytest.raises(ValidationError):
        PromptComponent(name="TestRole", type=ComponentType.ROLE, content="test", priority=11)


def test_prompt_component_render() -> None:
    """Test PromptComponent render method."""
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="You are a {role}.")
    rendered = component.render(role="doctor")
    assert rendered == "You are a doctor."


def test_prompt_configuration_initialization() -> None:
    """Test PromptConfiguration initialization."""

    class TestModel(BaseModel):
        foo: str

    config = PromptConfiguration(
        system_message="System", user_message="User", response_model=TestModel, provenance_metadata={"role": "TestRole"}
    )
    assert config.system_message == "System"
    assert config.user_message == "User"
    assert config.response_model == TestModel
    assert config.max_retries == 3
    assert config.provenance_metadata == {"role": "TestRole"}


def test_prompt_configuration_optional_response_model() -> None:
    """Test PromptConfiguration with optional response_model."""
    config = PromptConfiguration(
        system_message="System", user_message="User", response_model=None, provenance_metadata={}
    )
    assert config.response_model is None


def test_prompt_configuration_max_retries_validation() -> None:
    """Test PromptConfiguration max_retries validation."""
    with pytest.raises(ValidationError):
        PromptConfiguration(
            system_message="System", user_message="User", response_model=None, provenance_metadata={}, max_retries=-1
        )
