import subprocess
import sys


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def lint() -> None:
    run(["flake8", "src"])


def typecheck() -> None:
    run(["mypy", "src"])


def commitlint() -> None:
    run(["npx", "commitlint", "--from=HEAD~1", "--to=HEAD"])


def install_hooks() -> None:
    run(["pre-commit", "install"])
    run(["pre-commit", "install", "--hook-type", "commit-msg"])


def check() -> None:
    lint()
    typecheck()


def ci() -> None:
    check()
    commitlint()
