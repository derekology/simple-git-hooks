"""
Commit-msg hook to check the commit message format against regex patterns.

One or multiple acceptance/rejection patterns can be supplied as arguments.
"""

from typing import List, Tuple

from enum import Enum
import argparse
import re


class TextStyle(Enum):
    """
    Enumeration for combining foreground, background, and attribute codes.
    """

    DEFAULT = "\033[0m"  # Reset all styles
    WARN = "\033[1;33m"  # Bold Yellow
    ERROR = "\033[1;31m"  # Bold Red
    OK = "\033[1;32m"  # Bold Green


def check_commit_msg(
    commit_msg: str,
    accept_patterns: List[str] = None,
    reject_patterns: List[str] = None,
) -> Tuple[int, str]:
    """
    Check a commit message against provided acceptance and rejection patterns.

    :param commit_msg: the commit message to check (str)
    :param accept_patterns: a list of regular expressions to accept the message (List[str], defaults to ['.*']) (optional)
    :param reject_patterns: a list of regular expressions to reject the message (List[str], defaults to []) (optional)

    :return: an integer exit code:
             - 0: Commit message accepted
             - 1: Commit message did not match any of the acceptance patterns supplied
             - 2: Commit message matched a rejection pattern
             - 99: Error occurred during compilation of regex patterns
    """
    if not commit_msg:
        msg = "Commit message is empty"
        return 1, msg

    compiled_accept_patterns = []
    for pattern in accept_patterns or [".*"]:
        try:
            compiled_accept_patterns.append(re.compile(pattern))
        except re.error as e:
            msg = f"Error compiling accept pattern: {pattern} ({e})"
            return 99, msg

    compiled_reject_patterns = []
    for pattern in reject_patterns or []:
        try:
            compiled_reject_patterns.append(re.compile(pattern))
        except re.error as e:
            msg = f"Error compiling reject pattern: {pattern} ({e})"
            return 99, msg

    for pattern in compiled_reject_patterns:
        if pattern.match(commit_msg):
            msg = f"Commit message matched rejection pattern: {pattern.pattern}"
            return 2, msg

    for pattern in compiled_accept_patterns:
        if pattern.match(commit_msg):
            return 0, ""

    msg = "Commit message did not match any of the acceptance patterns supplied"
    return 1, msg


def get_commit_msg(filepath: str) -> str:
    """
    Read the commit message content from a file.

    :param filepath: path to the file containing the commit message (str)
    :return: the commit message content read from the file (str)
    """
    with open(filepath) as f:
        return f.read().strip()


def parse_args() -> argparse.Namespace:
    """
    Parse arguments.

    :return: a Namespace object containing parsed arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a", "--accept", action="append", type=str, help="Regex pattern(s) to accept"
    )
    parser.add_argument(
        "-r", "--reject", action="append", type=str, help="Regex pattern(s) to reject"
    )
    parser.add_argument(
        "--exit-zero", action="store_true", help="Exit code 0 regardless of results"
    )
    parser.add_argument("filepath", help="Path to the commit_msg file")

    return parser.parse_args()


def main():
    """
    Drive the program.
    """
    args = parse_args()
    commit_msg = get_commit_msg(filepath=args.filepath)
    result, msg = check_commit_msg(
        commit_msg=commit_msg, accept_patterns=args.accept, reject_patterns=args.reject
    )

    error_prefix = (
        f"{TextStyle.ERROR.value}[ERR]{TextStyle.DEFAULT.value}"
        if not args.exit_zero
        else f"{TextStyle.WARN.value}[WARN]{TextStyle.DEFAULT.value}"
    )

    if result != 0:
        print(error_prefix, msg)

    if args.exit_zero:
        exit(0)

    exit(result)


if __name__ == "__main__":
    main()
