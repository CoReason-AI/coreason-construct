import pytest
from pydantic import BaseModel, ValidationError

from coreason_construct.schemas.base import ComponentType, PromptComponent, PromptConfiguration


class MockResponse(BaseModel):
    data: str


def test_component_type_values() -> None:
    assert ComponentType.ROLE == "ROLE"
    assert ComponentType.CONTEXT == "CONTEXT"
    assert ComponentType.MODE == "MODE"
    assert ComponentType.DATA == "DATA"
    assert ComponentType.PRIMITIVE == "PRIMITIVE"


def test_prompt_component_creation() -> None:
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="You are a {role}.", priority=5)
    assert component.name == "TestRole"
    assert component.type == ComponentType.ROLE
    assert component.content == "You are a {role}."
    assert component.priority == 5


def test_prompt_component_defaults() -> None:
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="You are a helper.")
    assert component.priority == 1


def test_prompt_component_priority_validation() -> None:
    # Valid boundaries
    PromptComponent(name="Test", type=ComponentType.ROLE, content="", priority=1)
    PromptComponent(name="Test", type=ComponentType.ROLE, content="", priority=10)

    # Invalid boundaries
    with pytest.raises(ValidationError):
        PromptComponent(name="Test", type=ComponentType.ROLE, content="", priority=0)
    with pytest.raises(ValidationError):
        PromptComponent(name="Test", type=ComponentType.ROLE, content="", priority=11)


def test_prompt_component_render() -> None:
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="You are a {role}.")
    rendered = component.render(role="Doctor")
    assert rendered == "You are a Doctor."


def test_prompt_component_render_missing_kwargs() -> None:
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="You are a {role}.")
    with pytest.raises(KeyError):
        component.render()


def test_prompt_component_render_extra_kwargs() -> None:
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="You are a {role}.")
    rendered = component.render(role="Doctor", extra="Ignored")
    assert rendered == "You are a Doctor."


def test_prompt_component_render_complex_types() -> None:
    component = PromptComponent(name="TestRole", type=ComponentType.ROLE, content="Value: {val}")
    # Integer
    assert component.render(val=123) == "Value: 123"
    # Object
    obj = object()
    assert component.render(val=obj) == f"Value: {str(obj)}"


def test_prompt_component_render_escaped_braces() -> None:
    component = PromptComponent(name="TestJSON", type=ComponentType.DATA, content='JSON: {{ "key": "{val}" }}')
    rendered = component.render(val="value")
    assert rendered == 'JSON: { "key": "value" }'


def test_prompt_component_render_malformed() -> None:
    # Unmatched brace
    component = PromptComponent(name="TestBad", type=ComponentType.ROLE, content="Hello {world")
    with pytest.raises(ValueError):
        component.render(world="Earth")


def test_prompt_configuration_creation() -> None:
    config = PromptConfiguration(
        system_message="System", user_message="User", response_model=MockResponse, provenance_metadata={"role": "Test"}
    )
    assert config.system_message == "System"
    assert config.user_message == "User"
    assert config.response_model == MockResponse
    assert config.max_retries == 3
    assert config.provenance_metadata == {"role": "Test"}


def test_prompt_configuration_optional_model() -> None:
    config = PromptConfiguration(
        system_message="System", user_message="User", response_model=None, provenance_metadata={}
    )
    assert config.response_model is None


def test_prompt_configuration_validation() -> None:
    # Invalid max_retries (negative)
    with pytest.raises(ValidationError):
        PromptConfiguration(
            system_message="Sys", user_message="Usr", response_model=None, provenance_metadata={}, max_retries=-1
        )
