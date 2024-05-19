"""Tests for check_branch_name hook."""

import pytest
import re
import sys
import subprocess
from unittest.mock import Mock, patch

from hooks.check_branch_name import (
    check_branch_name,
    get_current_branch_name,
    parse_args,
    main,
)


def test_check_branch_name_valid_patterns():
    """Test check_branch_name with valid branch name."""
    patterns = ["This is a pattern", "This is another pattern"]

    # Matches acceptance pattern
    result, msg = check_branch_name("This is a pattern", accept_patterns=patterns)
    assert result == 0, msg
    assert msg == ""

    result, msg = check_branch_name("This is another pattern", accept_patterns=patterns)
    assert result == 0, msg
    assert msg == ""

    # Does not match rejection pattern
    result, msg = check_branch_name("This does not match", reject_patterns=patterns)
    assert result == 0, msg
    assert msg == ""


def test_check_branch_name_invalid_patterns():
    """Test check_branch_name with invalid commit message."""
    patterns = ["This is a pattern"]

    # Does not match acceptance pattern
    result, msg = check_branch_name(
        "This is an invalid message", accept_patterns=patterns
    )
    assert result == 1, msg
    assert "Branch name did not match any of the acceptance patterns supplied" in msg

    # Matches rejection pattern
    result, msg = check_branch_name("This is a pattern", reject_patterns=patterns)
    assert result == 2, msg
    assert "Branch name matched rejection pattern" in msg


def test_check_branch_name_compilation_error():
    with patch.object(re, "compile") as mock_compile:
        mock_compile.side_effect = re.error("This is a mock compilation error")
        result, msg = check_branch_name("Some message", accept_patterns=["[invalid]"])
        assert result == 99, msg
        assert "Error compiling accept pattern" in msg


def test_get_current_branch_name_success(mocker):
    """Test successful retrieval of the current branch name."""
    expected_branch_name = "master"
    mocker.patch.object(
        subprocess,
        "run",
        return_value=subprocess.CompletedProcess(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            returncode=0,
            stdout=f"{expected_branch_name}\n",
        ),
    )
    branch_name = get_current_branch_name()
    assert branch_name == expected_branch_name


def test_get_current_branch_name_error(mocker):
    """Test getting an empty string when a subprocess error occurs."""
    mocker.patch.object(
        subprocess,
        "run",
        side_effect=subprocess.CalledProcessError(cmd="run", returncode=1),
    )
    branch_name = get_current_branch_name()
    assert branch_name == ""


def test_get_current_branch_name_no_git(mocker):
    """Test getting an empty string when the git command is not found."""
    mocker.patch.object(subprocess, "run", side_effect=FileNotFoundError)
    branch_name = get_current_branch_name()
    assert branch_name == ""


def test_single_accept():
    """Test parsing with a single accept pattern."""
    original_argv = sys.argv
    sys.argv = ["check_branch_name.py", "-a", "feat/.*"]
    args = parse_args()
    sys.argv = original_argv
    assert "feat/.*" in args.accept
    assert len(args.accept) == 1


def test_multiple_accept():
    """Test parsing with multiple accept patterns."""
    original_argv = sys.argv
    sys.argv = [
        "check_branch_name.py",
        "-a",
        "feat/.*",
        "-a",
        "fix/.*",
    ]
    args = parse_args()
    sys.argv = original_argv
    assert set(["feat/.*", "fix/.*"]) == set(args.accept)
    assert len(args.accept) == 2


def test_single_reject():
    """Test parsing with a single reject pattern."""
    original_argv = sys.argv
    sys.argv = ["check_branch_name.py", "-r", "main"]
    args = parse_args()
    sys.argv = original_argv
    assert "main" in args.reject
    assert len(args.reject) == 1


def test_multiple_reject():
    """Test parsing with multiple reject patterns."""
    original_argv = sys.argv
    sys.argv = ["check_branch_name.py", "-r", "main", "-r", "master"]
    args = parse_args()
    sys.argv = original_argv
    assert set(["main", "master"]) == set(args.reject)
    assert len(args.reject) == 2


def test_mixed_args():
    """Test parsing with a mix of accept and reject patterns."""
    original_argv = sys.argv
    sys.argv = ["check_branch_name.py", "-a", "fix/.*", "-r", "main", "-a", "feat/.*"]
    args = parse_args()
    sys.argv = original_argv
    assert set(["fix/.*", "feat/.*"]) == set(args.accept)
    assert len(args.accept) == 2
    assert "main" in args.reject
    assert len(args.reject) == 1


def test_main_success(mocker):
    """Test main function with successful execution."""
    # Mock check_branch_name and get_current_branch_name to avoid actual file operations
    mocked_args = Mock(filepath="test_file.txt")
    mocker.patch("hooks.check_branch_name.parse_args", return_value=mocked_args)
    mocker.patch(
        "hooks.check_branch_name.get_current_branch_name", return_value="A message"
    )
    mocker.patch("hooks.check_branch_name.check_branch_name", return_value=(0, ""))
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.type == SystemExit
    assert excinfo.value.code == 0


def test_main_error(mocker, capsys):
    """Test main function with an error during check_branch_name."""
    mocked_args = Mock(filepath="test_file.txt")
    mocker.patch("hooks.check_branch_name.parse_args", return_value=mocked_args)
    mocker.patch(
        "hooks.check_branch_name.get_current_branch_name", return_value="A message"
    )
    mocker.patch(
        "hooks.check_branch_name.check_branch_name", return_value=(1, "An error")
    )
    with pytest.raises(SystemExit):
        main()
    assert capsys.readouterr()
