from coreason_construct.schemas.base import ComponentType, PromptComponent


def test_prompt_component_render() -> None:
    comp = PromptComponent(name="Test", type=ComponentType.CONTEXT, content="Hello {name}", priority=1)
    assert comp.render(name="World") == "Hello World"
