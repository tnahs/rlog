#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

import tomllib


APP_NAME = "bump"

ALLOWED_BUMP_LEVELS = {
    "major",
    "minor",
    "patch",
    "alpha",
    "beta",
    "dev",
    "final",
    "post",
    "rc",
}


def is_tree_dirty() -> bool:
    result = subprocess.run(
        [
            "git",
            "status",
            "--porcelain",
        ],
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    )

    return bool(result.stdout.strip())


def red(text: str) -> str:
    return f"\033[31;49m{text}\033[0m"


def green(text: str) -> str:
    return f"\033[32;49m{text}\033[0m"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        add_help=False,
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent(
            f"""
            Bump the package version and tag the latest commit.

            \033[4mUsage:\033[0m
              {APP_NAME} [OPTIONS] <level>

            \033[4mArguments:\033[0m
              level LEVEL  Version bump level.

            \033[4mOptions:\033[0m
              -h, --help     Show help
              -v, --version  Print version

            \033[4mAvailable Bump Levels:\033[0m
              major
              minor
              patch
              alpha
              beta
              dev
              final
              post
              rc
        """.rstrip()
        ),
    )
    parser.add_argument(
        "level",
        choices=ALLOWED_BUMP_LEVELS,
        type=str,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()

    if is_tree_dirty():
        print(red("Working tree is dirty. Commit/stash changes before running."))
        sys.exit(-1)

    subprocess.run(
        [
            "uv",
            "version",
            "--bump",
            args.level,
        ],
        check=True,
    )

    with Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)

    version_tag = data["project"]["version"]
    version_tag = f"v{version_tag}"

    subprocess.run(
        [
            "git",
            "add",
            "*",
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"bump version to {version_tag}",
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "tag",
            version_tag,
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "push",
            "origin",
            "main",
        ],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "push",
            "origin",
            version_tag,
        ],
        check=True,
    )

    print(f"\nBumped to: {green(version_tag)}")


if __name__ == "__main__":
    main()
