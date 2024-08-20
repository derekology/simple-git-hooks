# Simple Git Hooks

Git hook scripts that make development a little easier. Designed to be installed and run through [pre-commit](https://pre-commit.com/).

To use:

1. Install `pre-commit` by following [these instructions](https://pre-commit.com/#install)
2. Add the following to `.pre-commit-config.yaml` file in your project root

```
repos:
-    repo: https://github.com/derekology/simple-git-hooks
     rev: v1.2.0
     hooks:
     -    id: ....
```

## Hooks available

**`check-commit-msg`**

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

**`check-branch-name`**

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

**`check-for-pattern`**

Checks whether patterns (provided as regular expressions), are present in the committed files. Offers both required and rejection sequences.

Use `-EsC-` as an escape sequence when necessary.

Arguments:

- `-q` or `--require`: regex pattern to require in each file (can be used multiple times).
- `-r` or `--reject`: regex pattern to reject in each file (can be used multiple times).
- `--exit-zero`: pass the hook regardless of result. Use with hook-level flag `verbose: True` to print a warning.

Sample usage:

```
-   id: check-for-pattern
    verbose: True
    args:
    -    "--require=-EsC-(c-EsC-) 2024 Company Name"
    -    "--reject=#TODO"
    -    "--exit-zero"
```

## Known issues

**`check-commit-msg`**

- Does not run on Windows due to limitations with commit message hooks on the platform.

**`check-branch-name`**

- Does not work when run on the very first commit to a new repository.
