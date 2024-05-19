"""Tests for check_commit_msg hook."""

import io
import pytest
import re
import sys
from unittest.mock import Mock, patch

from hooks.check_commit_msg import check_commit_msg, get_commit_msg, main


def test_check_commit_msg_valid_patterns():
    """Test check_commit_msg with valid commit message."""
    patterns = ["This is a pattern"]

    # Matches acceptance pattern
    result, msg = check_commit_msg("This is a pattern", accept_patterns=patterns)
    assert result == 0, msg
    assert msg == ""

    # Does not match rejection pattern
    result, msg = check_commit_msg("This does not match", reject_patterns=patterns)
    assert result == 0, msg
    assert msg == ""


def test_check_commit_msg_invalid_patterns():
    """Test check_commit_msg with invalid commit message."""
    patterns = ["This is a pattern"]

    # Does not match acceptance pattern
    result, msg = check_commit_msg(
        "This is an invalid message", accept_patterns=patterns
    )
    assert result == 1, msg
    assert "Commit message did not match any of the acceptance patterns supplied" in msg

    # Matches rejection pattern
    result, msg = check_commit_msg("This is a pattern", reject_patterns=patterns)
    assert result == 2, msg
    assert "Commit message matched rejection pattern" in msg


def test_check_commit_msg_compilation_error():
    with patch.object(re, "compile") as mock_compile:
        mock_compile.side_effect = re.error("This is a mock compilation error")
        result, msg = check_commit_msg("Some message", accept_patterns=["[invalid]"])
        assert result == 99, msg
        assert "Error compiling accept pattern" in msg


def test_check_commit_msg_empty_message():
    """Test check_commit_msg with an empty commit message."""
    result, msg = check_commit_msg("")
    assert result == 1
    assert "Commit message is empty" in msg


def test_get_commit_msg_success():
    """Test get_commit_msg with a valid file path."""
    with patch("builtins.open") as mock_file:
        mock_file.return_value = mock_file.__enter__.return_value = io.StringIO(
            "This is a commit message"
        )
        message = get_commit_msg("some/file/path.txt")
        assert message == "This is a commit message"


def test_get_commit_msg_file_not_found():
    """Test get_commit_msg with a non-existent file."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            get_commit_msg("non-existent.txt")


def test_main_success(mocker):
    """Test main function with successful execution."""
    # Mock check_commit_msg and get_commit_msg to avoid actual file operations
    mocked_args = Mock(filepath="test_file.txt")
    mocker.patch("check_commit_msg.parse_args", return_value=mocked_args)
    mocker.patch("check_commit_msg.get_commit_msg", return_value="A message")
    mocker.patch("check_commit_msg.check_commit_msg", return_value=(0, ""))
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.type == SystemExit
    assert excinfo.value.code == 0


def test_main_error(mocker, capsys):
    """Test main function with an error during check_commit_msg."""
    mocked_args = Mock(filepath="test_file.txt")
    mocker.patch("check_commit_msg.parse_args", return_value=mocked_args)
    mocker.patch("check_commit_msg.get_commit_msg", return_value="A message")
    mocker.patch("check_commit_msg.check_commit_msg", return_value=(1, "An error"))
    with pytest.raises(SystemExit):
        main()
    assert capsys.readouterr()
