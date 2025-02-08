"""Update copyright headers in source files."""

import datetime
import os
import re
from pathlib import Path
from typing import List, Optional


COPYRIGHT_HEADERS = {
    # Root project - Proprietary
    "root": [
        "# CONFIDENTIAL AND PROPRIETARY",
        "#",
        f"# Copyright (c) {datetime.datetime.now().year} AudioKit.ai. All rights reserved.",
        "#",
        "# This software is confidential and proprietary.",
        "",
    ],
    # AudioKit AI package - MIT
    "audiokit_ai": [
        "# MIT License",
        "#",
        f"# Copyright (c) {datetime.datetime.now().year} AudioKit.ai",
        "#",
        "# This file is part of the AudioKit AI package.",
        "",
    ],
}

EXTENSIONS = {".py", ".pyi", ".pyx", ".pxd"}


def find_files(directory: Path, package: Optional[str] = None) -> List[Path]:
    """Find all Python source files in directory."""
    files = []
    for root, _, filenames in os.walk(directory):
        root_path = Path(root)
        if "venv" in root_path.parts or ".git" in root_path.parts:
            continue
        for filename in filenames:
            if Path(filename).suffix in EXTENSIONS:
                files.append(root_path / filename)
    return files


def update_copyright(file_path: Path, header_lines: List[str]) -> bool:
    """Update copyright header in file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Remove existing copyright header
    content = re.sub(
        r"^(#.*Copyright.*\n)+\s*",
        "",
        content,
        flags=re.MULTILINE,
    )

    # Add new header
    new_content = "\n".join(header_lines) + "\n" + content

    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def main() -> None:
    """Update copyright headers in all source files."""
    root = Path(__file__).parent.parent

    # Update root project files
    root_files = find_files(root)
    for file_path in root_files:
        if "packages" not in file_path.parts:
            print(f"Updating root file: {file_path}")
            update_copyright(file_path, COPYRIGHT_HEADERS["root"])

    # Update AudioKit AI package files
    audiokit_dir = root / "packages" / "audiokit_ai"
    audiokit_files = find_files(audiokit_dir)
    for file_path in audiokit_files:
        print(f"Updating AudioKit AI file: {file_path}")
        update_copyright(file_path, COPYRIGHT_HEADERS["audiokit_ai"])


if __name__ == "__main__":
    main()
