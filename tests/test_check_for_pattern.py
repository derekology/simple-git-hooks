import pytest
from hooks.check_for_pattern import check_patterns_in_file, main


# Utility function to create a temporary file with content
@pytest.fixture
def temp_file(tmpdir):
    def _temp_file(content):
        file = tmpdir.join("temp_file.txt")
        file.write(content)
        return str(file)
    return _temp_file


# Test regex issues
def test_invalid_reject_pattern(temp_file):
    file_path = temp_file("This file has some content.")
    result, msg = check_patterns_in_file(file_path, reject_patterns=["[invalid["])
    assert result == 98
    assert "Invalid reject pattern" in msg


def test_invalid_accept_pattern(temp_file):
    file_path = temp_file("This file has some content.")
    result, msg = check_patterns_in_file(file_path, required_patterns=["[invalid["])
    assert result == 98
    assert "Invalid require pattern" in msg


def test_custom_escape_sequence_replacement(temp_file):
    file_path = temp_file("(c) [r]")

    # Escape sequence is "-EsC-"
    required_sequence = "-EsC-(c-EsC-)"
    reject_sequence = "-EsC-[r-EsC-]"
    
    result, _ = check_patterns_in_file(file_path, required_patterns=[required_sequence])
    assert result == 0
    
    result, _ = check_patterns_in_file(file_path, reject_patterns=[reject_sequence])
    assert result == 2


# Test basic functionality
def test_reject_pattern_found(temp_file):
    file_path = temp_file("This file contains a reject pattern.")
    result, msg = check_patterns_in_file(file_path, reject_patterns=["reject pattern"])
    assert result == 2
    assert "Rejected pattern 'reject pattern' found" in msg


def test_no_reject_pattern_no_accept(temp_file):
    file_path = temp_file("This file is clean of any patterns.")
    result, msg = check_patterns_in_file(file_path, reject_patterns=["reject pattern"])
    assert result == 0
    assert msg == ""


def test_accept_pattern_found(temp_file):
    file_path = temp_file("This file contains the correct pattern.")
    result, msg = check_patterns_in_file(file_path, required_patterns=["correct pattern"])
    assert result == 0
    assert msg == ""


def test_accept_pattern_not_found(temp_file):
    file_path = temp_file("This file is missing a required pattern.")
    result, msg = check_patterns_in_file(file_path, required_patterns=["This is required"])
    assert result == 1
    assert "Required pattern 'This is required' not found" in msg


def test_no_reject_pattern_and_accept_pattern(temp_file):
    file_path = temp_file("This file contains the correct pattern.")
    result, msg = check_patterns_in_file(
        file_path, required_patterns=["correct pattern"], reject_patterns=["reject pattern"]
    )
    assert result == 0
    assert msg == ""


def test_no_reject_pattern_no_accept_pattern(temp_file):
    file_path = temp_file("This file has no relevant patterns.")
    result, msg = check_patterns_in_file(
        file_path, required_patterns=["correct pattern"], reject_patterns=["reject pattern"]
    )
    assert result == 1
    assert "Required pattern 'correct pattern' not found" in msg


def test_exit_zero(temp_file, monkeypatch):
    file_path = temp_file("This file is missing the correct pattern.")
    monkeypatch.setattr("argparse._sys.argv", ["check_for_pattern.py", "--exit-zero", "-q", "correct pattern", file_path])
    
    with pytest.raises(SystemExit) as excinfo:
        main()
    
    assert excinfo.value.code == 0


# Test multiple files
def test_one_file_fails_one_file_passes(temp_file, monkeypatch):
    file1 = temp_file("This file contains the required pattern.")
    file2 = temp_file("This file is missing the correct pattern.")
    
    monkeypatch.setattr("argparse._sys.argv", ["check_for_pattern.py", "-q", "required pattern", file1, file2])
    
    with pytest.raises(SystemExit) as excinfo:
        main()
    
    assert excinfo.value.code == 1


def test_all_files_pass(temp_file, monkeypatch):
    file1 = temp_file("This file contains the correct pattern.")
    file2 = temp_file("Another file with the correct pattern.")
    
    monkeypatch.setattr("argparse._sys.argv", ["check_for_pattern.py", "-q", "correct pattern", file1, file2])
    
    with pytest.raises(SystemExit) as excinfo:
        main()
    
    assert excinfo.value.code == 0


def test_all_files_fail(temp_file, monkeypatch):
    file1 = temp_file("This file is missing the correct pattern.")
    file2 = temp_file("Another file without the correct pattern.")
    
    monkeypatch.setattr("argparse._sys.argv", ["check_for_pattern.py", "-q", "This is required", file1, file2])
    
    with pytest.raises(SystemExit) as excinfo:
        main()
    
    assert excinfo.value.code == 1
