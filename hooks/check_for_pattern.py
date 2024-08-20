"""
Pre-commit hook to check for the presence of specified regex patterns in each file being committed.

One or multiple required/reject sequences can be supplied as arguments.
"""

from typing import List, Tuple

from enum import Enum
import argparse
import os
import re


CONFIG_FILE_NAME = ".pre-commit-config.yaml"


class TextStyle(Enum):
    """
    Enumeration for PASS/WARN/ERR colour codes.
    """

    DEFAULT = "\033[0m"  # Reset all styles
    WARN = "\033[1;33m"  # Bold Yellow
    ERROR = "\033[1;31m"  # Bold Red
    OK = "\033[1;32m"  # Bold Green


def check_patterns_in_file(
    filepath: str, required_patterns: List[str] = None, reject_patterns: List[str] = None
) -> Tuple[int, str]:
    """
    Check if all accept patterns are present and no reject patterns are present in the file.

    :param filepath: path to the file being checked (str)
    :param accept_patterns: list of regex patterns to check for (List[str], optional)
    :param reject_patterns: list of regex patterns to reject (List[str], optional)

    :return: a tuple with an integer exit code:
             - 0: All accept patterns found and no reject patterns found
             - 1: One or more accept patterns not found
             - 2: One or more reject patterns found
             - 98: Invalid regex pattern encountered
             - 99: Error occurred during file reading
    """
    try:
        with open(filepath, "r") as f:
            content = f.read()

        if reject_patterns:
            for pattern in reject_patterns:
                pattern = pattern.replace("-EsC-", "\\")
                try:
                    if re.search(pattern, content):
                        msg = f"Rejected pattern '{pattern}' found in file: {filepath}"
                        return 2, msg
                except re.error as e:
                    msg = f"Invalid reject pattern '{pattern}' in file: {filepath} ({e})"
                    return 98, msg

        if required_patterns:
            for pattern in required_patterns:
                pattern = pattern.replace("-EsC-", "\\")
                try:
                    if not re.search(pattern, content):
                        msg = f"Required pattern '{pattern}' not found in file: {filepath}"
                        return 1, msg
                except re.error as e:
                    msg = f"Invalid require pattern '{pattern}' in file: {filepath} ({e})"
                    return 98, msg

        return 0, ""

    except Exception as e:
        msg = f"Error reading file: {filepath} ({e})"
        return 99, msg


def parse_args() -> argparse.Namespace:
    """
    Parse arguments.

    :return: a Namespace object containing parsed arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-q", "--require", action="append", type=str, required=False,
        help="Regex pattern(s) to require"
    )
    parser.add_argument(
        "-r", "--reject", action="append", type=str, required=False,
        help="Regex pattern(s) to reject"
    )
    parser.add_argument(
        "--exit-zero", action="store_true", help="Exit code 0 regardless of results"
    )
    parser.add_argument("files", nargs="+", help="Files to check")

    return parser.parse_args()


def main():
    """
    Drive the program.
    """
    args = parse_args()
    required_patterns = args.require
    reject_patterns = args.reject
    exit_code = 0

    for filepath in args.files:
        if CONFIG_FILE_NAME in filepath:
            continue

        if not os.path.isfile(filepath):
            print(
                f"{TextStyle.ERROR.value}[ERR]{TextStyle.DEFAULT.value} File not found: {filepath}"
            )
            exit_code = 99
            continue

        result, msg = check_patterns_in_file(
            filepath=filepath,
            required_patterns=required_patterns,
            reject_patterns=reject_patterns
        )

        if result != 0:
            error_prefix = (
                f"{TextStyle.ERROR.value}[ERR]{TextStyle.DEFAULT.value}"
                if not args.exit_zero
                else f"{TextStyle.WARN.value}[WARN]{TextStyle.DEFAULT.value}"
            )
            print(error_prefix, msg)
            if not args.exit_zero:
                exit_code = result

    if args.exit_zero:
        exit(0)

    exit(exit_code)


if __name__ == "__main__":
    main()
