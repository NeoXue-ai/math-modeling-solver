#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

SKILL_NAME = "math-modeling-solver"
TARGETS = {
    "codex": Path(".codex") / "skills" / SKILL_NAME,
    "claude": Path(".claude") / "skills" / SKILL_NAME,
}
IGNORED_NAMES = {
    ".git",
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    "CUMCM_Workspace",
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Install math-modeling-solver for Codex and Claude Code.")
    parser.add_argument(
        "--target",
        choices=["codex", "claude", "both"],
        default="both",
        help="Installation target.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skill source directory.",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="Home directory used to resolve platform skill paths.",
    )
    return parser.parse_args(argv)


def ignore_names(directory, names):
    return [name for name in names if name in IGNORED_NAMES or name.endswith(".pyc")]


def selected_targets(target):
    if target == "both":
        return ["codex", "claude"]
    return [target]


def install_to(source, destination):
    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        print(f"{SKILL_NAME} already installed at {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True, ignore=ignore_names)
    print(f"Installed {SKILL_NAME}: {destination}")


def main(argv=None):
    args = parse_args(argv)
    source = args.source
    if not (source / "SKILL.md").exists():
        print(f"source is not a skill directory: {source}")
        return 1

    for target in selected_targets(args.target):
        install_to(source, args.home / TARGETS[target])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
