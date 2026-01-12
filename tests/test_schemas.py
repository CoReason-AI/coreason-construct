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


def test_prompt_component_priority_validation() -> None:
    # Test lower bound
    with pytest.raises(ValidationError) as exc:
        PromptComponent(name="Test", type=ComponentType.ROLE, content="Content", priority=0)
    assert "Input should be greater than or equal to 1" in str(exc.value)

    # Test upper bound
    with pytest.raises(ValidationError) as exc:
        PromptComponent(name="Test", type=ComponentType.ROLE, content="Content", priority=11)
    assert "Input should be less than or equal to 10" in str(exc.value)


def test_prompt_component_render() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.ROLE, content="Hello, {name}!")
    rendered = component.render(name="World")
    assert rendered == "Hello, World!"


def test_prompt_component_render_missing_kwargs() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.ROLE, content="Hello, {name}!")
    with pytest.raises(KeyError):
        component.render()


def test_prompt_component_render_extra_kwargs() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.ROLE, content="Hello, {name}!")
    rendered = component.render(name="World", extra="IgnoreMe")
    assert rendered == "Hello, World!"


def test_prompt_component_render_escaped_braces() -> None:
    component = PromptComponent(name="TestComponent", type=ComponentType.ROLE, content="Hello, {{name}}!")
    rendered = component.render(name="World")
    # In python format, {{ escapes to {
    assert rendered == "Hello, {name}!"

    component_mixed = PromptComponent(
        name="Mixed", type=ComponentType.ROLE, content="Value: {val}, Escaped: {{escaped}}"
    )
    rendered_mixed = component_mixed.render(val="10")
    assert rendered_mixed == "Value: 10, Escaped: {escaped}"


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


def test_prompt_configuration_retries_validation() -> None:
    with pytest.raises(ValidationError) as exc:
        PromptConfiguration(
            system_message="System", user_message="User", response_model=None, provenance_metadata={}, max_retries=-1
        )
    assert "Input should be greater than or equal to 0" in str(exc.value)
