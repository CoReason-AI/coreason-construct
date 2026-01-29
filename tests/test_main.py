import json
from argparse import Namespace
from unittest.mock import patch

import pytest
from coreason_identity.models import UserContext

from coreason_construct.main import create_command, get_cli_context, main, resolve_command, visualize_command
from coreason_construct.schemas.base import ComponentType, PromptComponent


@pytest.fixture
def cli_context() -> UserContext:
    return get_cli_context()


@pytest.fixture
def components_file(tmp_path: object) -> str:
    # mypy might complain about tmp_path if not typed correctly as pytest specific
    # but usually 'object' or 'Any' is fine if we don't import pytest's types
    from pathlib import Path
    assert isinstance(tmp_path, Path)
    p = tmp_path / "components.json"
    comp = PromptComponent(name="TestComp", type=ComponentType.CONTEXT, content="test")
    p.write_text(json.dumps([comp.model_dump()]))
    return str(p)


def test_create_command(cli_context: UserContext, components_file: str, capsys: pytest.CaptureFixture[str]) -> None:
    args = Namespace(name="test_construct", components_file=components_file)
    create_command(args, cli_context)
    captured = capsys.readouterr()
    assert "Construct 'test_construct' created" in captured.out


def test_create_command_error(cli_context: UserContext, capsys: pytest.CaptureFixture[str]) -> None:
    args = Namespace(name="test_construct", components_file="non_existent.json")
    create_command(args, cli_context)
    captured = capsys.readouterr()
    assert "Error reading components file" in captured.err


def test_resolve_command(cli_context: UserContext, capsys: pytest.CaptureFixture[str]) -> None:
    args = Namespace(construct_id="test_construct", variables_file=None)
    resolve_command(args, cli_context)
    captured = capsys.readouterr()
    # Should output config json, check for keys
    assert "system_message" in captured.out


def test_resolve_command_with_vars(
    cli_context: UserContext, tmp_path: object, capsys: pytest.CaptureFixture[str]
) -> None:
    from pathlib import Path

    assert isinstance(tmp_path, Path)
    p = tmp_path / "vars.json"
    p.write_text(json.dumps({"test": "val"}))
    args = Namespace(construct_id="test_construct", variables_file=str(p))
    resolve_command(args, cli_context)
    captured = capsys.readouterr()
    assert "system_message" in captured.out


def test_resolve_command_error(cli_context: UserContext, capsys: pytest.CaptureFixture[str]) -> None:
    args = Namespace(construct_id="test_construct", variables_file="non_existent.json")
    resolve_command(args, cli_context)
    captured = capsys.readouterr()
    assert "Error reading variables file" in captured.err


def test_visualize_command(cli_context: UserContext, capsys: pytest.CaptureFixture[str]) -> None:
    args = Namespace(construct_id="test_construct")
    visualize_command(args, cli_context)
    captured = capsys.readouterr()
    assert "construct_id" in captured.out


def test_main_cli_create(components_file: str, capsys: pytest.CaptureFixture[str]) -> None:
    with patch("sys.argv", ["main.py", "create", "--name", "test", "--components-file", components_file]):
        main()
    captured = capsys.readouterr()
    assert "Construct 'test' created" in captured.out


def test_main_cli_resolve(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("sys.argv", ["main.py", "resolve", "--construct-id", "test"]):
        main()
    captured = capsys.readouterr()
    assert "system_message" in captured.out


def test_main_cli_visualize(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("sys.argv", ["main.py", "visualize", "--construct-id", "test"]):
        main()
    captured = capsys.readouterr()
    assert "construct_id" in captured.out
