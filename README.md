# Simple Git Hooks
Git hook scripts that make development a little easier. Designed to be installed and run through [pre-commit](https://pre-commit.com/).

To use:
1. Install `pre-commit` by following [these instructions](https://pre-commit.com/#install)
2. Add the following to `.pre-commit-config.yaml` file in your project root
```
-    repo: https://github.com/derekology/simple-git-hooks
     rev: v1.1.0
     hooks:
     -    id: ....
```
## Hooks available
`check-commit-msg`

Validates commit messages against provided regular expressions. Offers both acceptance and rejection patterns for fine-grained control over commit message format.

Arguments:
- `-a` or `--accept`: regex pattern to accept if matched (can be used multiple times).
- `-r` or `--reject`: regex pattern to reject if matched (can be used multiple times).
- `--exit-zero`: pass the hook regardless of result. Use with hook-level flag `verbose: True` to print a warning.

Sample usage:
```
-   id: check-commit-msg
    verbose: True
    args:
    -    "--accept=^FIX: .*"
    -    "--accept=^FEATURE: .*"
    -    "--reject=^BUGFIX: .*"
    -    "--exit-zero"
```


`check-branch-name`

Validates branch name against provided regular expressions, similar to the `check-commit-msg` hook. Offers both acceptance and rejection patterns.

Arguments:
- `-a` or `--accept`: regex pattern to accept if matched (can be used multiple times).
- `-r` or `--reject`: regex pattern to reject if matched (can be used multiple times).
- `--exit-zero`: pass the hook regardless of result. Use with hook-level flag `verbose: True` to print a warning.

Sample usage:
```
-   id: check-branch-name
    verbose: True
    args:
    -    "--accept=^fix/.*"
    -    "--accept=^feat/.*"
    -    "--reject=main"
    -    "--exit-zero"
```