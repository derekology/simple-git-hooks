"""
Pre-commit hook to check the branch name format against regex patterns.

One or multiple acceptance/rejection patterns can be supplied as arguments.
"""

from typing import List, Tuple

from enum import Enum
import argparse
import re
import subprocess


class TextStyle(Enum):
    """
    Enumeration for PASS/WARN/ERR colour codes.
    """

    DEFAULT = "\033[0m"  # Reset all styles
    WARN = "\033[1;33m"  # Bold Yellow
    ERROR = "\033[1;31m"  # Bold Red
    OK = "\033[1;32m"  # Bold Green


def check_branch_name(
    branch_name: str,
    accept_patterns: List[str] = None,
    reject_patterns: List[str] = None,
) -> Tuple[int, str]:
    """
    Check branch name against provided acceptance and rejection patterns.

    :param branch_name: The branch name to check (str)
    :param accept_patterns: a list of regular expressions to accept the branch name (List[str], defaults to ['.*']) (optional)
    :param reject_patterns: a list of regular expressions to reject the branch name (List[str], defaults to []) (optional)

    :return: an integer exit code:
             - 0: Branch name accepted
             - 2: Branch name matched a rejection pattern
             - 1: Branch name did not match any of the acceptance patterns supplied
             - 99: Error occurred during compilation of regex patterns
    """
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
        if pattern.match(branch_name):
            msg = f"Branch name matched rejection pattern: {pattern.pattern}"
            return 2, msg

    for pattern in compiled_accept_patterns:
        if pattern.match(branch_name):
            return 0, ""

    msg = "Branch name did not match any of the acceptance patterns supplied"
    return 1, msg


def get_current_branch_name() -> str:
  """Gets the current Git branch name using the `git` command.

  :return: the current branch name, or None if there's an error or no branch (str)
  """
  try:
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    result.check_returncode()
    return result.stdout.strip()
  except (subprocess.CalledProcessError, FileNotFoundError):
    return ""


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

    return parser.parse_args()


def main():
    """
    Drive the program.
    """
    args = parse_args()
    branch_name = get_current_branch_name()

    if not branch_name:
        result = 1
        msg = "Could not get branch name"
    else:
        result, msg = check_branch_name(
            branch_name=branch_name, accept_patterns=args.accept, reject_patterns=args.reject
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
