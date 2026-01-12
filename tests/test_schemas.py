import pytest
from coreason_construct.schemas.base import ComponentType, PromptComponent, PromptConfiguration
from pydantic import BaseModel, ValidationError


class TestSchema(BaseModel):
    field: str


def test_component_type_enum() -> None:
    assert ComponentType.ROLE == "ROLE"
    assert ComponentType.CONTEXT == "CONTEXT"
    assert ComponentType.MODE == "MODE"
    assert ComponentType.DATA == "DATA"
    assert ComponentType.PRIMITIVE == "PRIMITIVE"


def test_prompt_component_initialization() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.ROLE, content="This is a {test}.", priority=5)
    assert component.name == "TestComponent"
    assert component.type == ComponentType.ROLE
    assert component.content == "This is a {test}."
    assert component.priority == 5


def test_prompt_component_default_priority() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.CONTEXT, content="Content")
    assert component.priority == 1


def test_prompt_component_render() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.ROLE, content="Hello, {name}!")
    rendered = component.render(name="World")
    assert rendered == "Hello, World!"


def test_prompt_component_render_missing_kwargs() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.ROLE, content="Hello, {name}!")
    with pytest.raises(KeyError):
        component.render()


def test_prompt_configuration_initialization() -> None:
    config = PromptConfiguration(
        system_message="System",
        user_message="User",
        response_model=TestSchema,
        max_retries=5,
        provenance_metadata={"role": "TestRole"},
    )
    assert config.system_message == "System"
    assert config.user_message == "User"
    assert config.response_model == TestSchema
    assert config.max_retries == 5
    assert config.provenance_metadata == {"role": "TestRole"}


def test_prompt_configuration_defaults() -> None:
    config = PromptConfiguration(
        system_message="System", user_message="User", response_model=None, provenance_metadata={}
    )
    assert config.max_retries == 3
    assert config.response_model is None


def test_prompt_configuration_validation() -> None:
    with pytest.raises(ValidationError):
        PromptConfiguration(
            system_message="System",
            user_message="User",
            # Missing response_model and provenance_metadata
        )  # type: ignore[call-arg]
