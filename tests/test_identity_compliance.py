import pytest
from coreason_identity.models import UserContext, SecretStr
from coreason_construct.weaver import Weaver
from coreason_construct.schemas.base import PromptComponent, ComponentType
from coreason_construct.contexts.library import ContextLibrary
from coreason_construct.roles.library import RoleLibrary, MedicalDirector
from coreason_construct.server import server, BlueprintRequest, CompilationResponse

@pytest.fixture
def mock_context() -> UserContext:
    return UserContext(
        user_id="test-user",
        email="test@coreason.ai",
        groups=["tester"],
        scopes=[],
        claims={"source": "test"}
    )

def test_weaver_identity_enforcement(mock_context: UserContext) -> None:
    weaver = Weaver()
    component = PromptComponent(name="TestComp", type=ComponentType.CONTEXT, content="test")

    # create_construct requires context
    with pytest.raises(ValueError, match="UserContext is required"):
        weaver.create_construct("test", [component], context=None)  # type: ignore

    # Should succeed with context
    weaver.create_construct("test", [component], context=mock_context)

    # resolve_construct requires context
    with pytest.raises(ValueError, match="UserContext is required"):
        weaver.resolve_construct("test", {}, context=None)  # type: ignore

    # Should succeed with context
    config = weaver.resolve_construct("test", {}, context=mock_context)
    assert config.provenance_metadata.get("owner_id") == "test-user"

def test_context_library_identity_enforcement(mock_context: UserContext) -> None:
    # register_context
    component = PromptComponent(name="TestCtx", type=ComponentType.CONTEXT, content="test")
    with pytest.raises(ValueError, match="UserContext is required"):
        ContextLibrary.register_context("TestCtx", component, context=None)  # type: ignore

    ContextLibrary.register_context("TestCtx", component, context=mock_context)

    # get_context
    with pytest.raises(ValueError, match="UserContext is required"):
        ContextLibrary.get_context("TestCtx", context=None)  # type: ignore

    ctx = ContextLibrary.get_context("TestCtx", context=mock_context)
    assert ctx.name == "TestCtx"


def test_role_library_identity_enforcement(mock_context: UserContext) -> None:
    # register_role
    with pytest.raises(ValueError, match="UserContext is required"):
        RoleLibrary.register_role("NewRole", MedicalDirector, context=None)  # type: ignore

    RoleLibrary.register_role("NewRole", MedicalDirector, context=mock_context)

    # get_role
    with pytest.raises(ValueError, match="UserContext is required"):
        RoleLibrary.get_role("NewRole", context=None)  # type: ignore

    role = RoleLibrary.get_role("NewRole", context=mock_context)
    assert role is not None
    assert role.name == "MedicalDirector"

def test_server_identity_enforcement(mock_context: UserContext) -> None:
    component = PromptComponent(name="TestComp", type=ComponentType.CONTEXT, content="test")
    request = BlueprintRequest(
        user_input="hello",
        components=[component]
    )

    # Handle request with context
    response = server.handle_request(request, context=mock_context)
    assert isinstance(response, CompilationResponse)
    assert response.token_count > 0
