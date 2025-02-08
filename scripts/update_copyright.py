"""Update copyright headers in source files."""

import argparse
import datetime
import os
import re
import json
from pathlib import Path
from typing import List, Optional, Set, Tuple, Dict, Any
import pathspec
from pathspec.patterns import GitWildMatchPattern


# File types to check
EXTENSIONS = {
    # Python files
    ".py",
    ".pyi",
    ".pyx",
    ".pxd",
    # Web files
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".css",
    ".scss",
    # Config files
    ".yml",
    ".yaml",
    ".toml",
    # Documentation
    ".md",
    ".rst",
}

# Package-specific configurations
PACKAGE_CONFIGS = {
    "root": {
        "header_type": "proprietary",
        "extensions": EXTENSIONS,
        "exclude_dirs": {"venv", ".git", "node_modules", "__pycache__"},
    },
    "audiokit_ai": {
        "header_type": "mit",
        "extensions": EXTENSIONS,
        "exclude_dirs": {"venv", ".git", "node_modules", "__pycache__"},
    },
    "audiokit_api": {
        "header_type": "proprietary",
        "extensions": EXTENSIONS,
        "exclude_dirs": {"venv", ".git", "node_modules", "__pycache__"},
    },
}

# Add report configuration
REPORT_CONFIG = {
    "output_formats": ["json", "markdown"],
    "report_dir": "reports/copyright",
    "checks": {
        "missing_headers": True,
        "outdated_years": True,
        "wrong_license": True,
        "style_violations": True,
    },
    "grouping": {
        "by_package": True,
        "by_license": True,
        "by_file_type": True,
    },
}


def get_copyright_years(content: str) -> Tuple[int, int]:
    """Extract copyright year or year range from content."""
    year_pattern = r"Copyright \(c\) (\d{4})(?:-(\d{4}))?"
    match = re.search(year_pattern, content)
    if not match:
        return (datetime.datetime.now().year, datetime.datetime.now().year)

    start_year = int(match.group(1))
    end_year = int(match.group(2)) if match.group(2) else start_year
    return (start_year, end_year)


def get_copyright_header(
    header_type: str,
    file_ext: str,
    start_year: Optional[int] = None,
) -> List[str]:
    """Generate copyright header based on file type and package."""
    current_year = datetime.datetime.now().year
    year_str = (
        f"{start_year}-{current_year}"
        if start_year and start_year < current_year
        else str(current_year)
    )

    # Get comment style for file type
    comment_start, comment_mid, comment_end = get_comment_style(file_ext)

    if header_type == "proprietary":
        return [
            f"{comment_start}CONFIDENTIAL AND PROPRIETARY",
            f"{comment_mid}",
            f"{comment_mid}Copyright (c) {year_str} AudioKit.ai. All rights reserved.",
            f"{comment_mid}",
            f"{comment_mid}This software is confidential and proprietary.",
            f"{comment_end}",
            "",
        ]
    else:  # MIT
        return [
            f"{comment_start}MIT License",
            f"{comment_mid}",
            f"{comment_mid}Copyright (c) {year_str} AudioKit.ai",
            f"{comment_mid}",
            f"{comment_mid}This file is part of the AudioKit AI package.",
            f"{comment_end}",
            "",
        ]


def get_comment_style(file_ext: str) -> Tuple[str, str, str]:
    """Get comment style for file type."""
    COMMENT_STYLES = {
        # Python-style
        ".py": ("# ", "# ", "# "),
        ".pyi": ("# ", "# ", "# "),
        ".pyx": ("# ", "# ", "# "),
        ".pxd": ("# ", "# ", "# "),
        # C-style
        ".js": ("/* ", " * ", " */"),
        ".ts": ("/* ", " * ", " */"),
        ".jsx": ("/* ", " * ", " */"),
        ".tsx": ("/* ", " * ", " */"),
        ".css": ("/* ", " * ", " */"),
        ".scss": ("/* ", " * ", " */"),
        # YAML-style
        ".yml": ("# ", "# ", "# "),
        ".yaml": ("# ", "# ", "# "),
        # TOML-style
        ".toml": ("# ", "# ", "# "),
        # Markdown-style
        ".md": ("<!--\n", "", "\n-->"),
        ".rst": (".. ", ".. ", ".. "),
    }
    return COMMENT_STYLES.get(file_ext, ("# ", "# ", "# "))


def get_gitignore_spec(root_dir: Path) -> pathspec.PathSpec:
    """Load gitignore patterns from all .gitignore files."""
    patterns = []

    # Walk up the directory tree looking for .gitignore files
    current_dir = root_dir
    while current_dir.parent != current_dir:  # Stop at root
        gitignore_file = current_dir / ".gitignore"
        if gitignore_file.exists():
            with open(gitignore_file, encoding="utf-8") as f:
                patterns.extend(
                    GitWildMatchPattern(line)
                    for line in f.read().splitlines()
                    if line and not line.startswith("#")
                )
        current_dir = current_dir.parent

    return pathspec.PathSpec(patterns)


def find_files(
    directory: Path,
    extensions: Set[str],
    exclude_dirs: Set[str],
) -> List[Path]:
    """Find all relevant files in directory, respecting .gitignore."""
    # Load gitignore patterns
    gitignore_spec = get_gitignore_spec(directory)

    files = []
    for root, dirs, filenames in os.walk(directory):
        # Filter out excluded directories
        dirs[:] = [
            d
            for d in dirs
            if d not in exclude_dirs
            and not gitignore_spec.match_file(str(Path(root) / d))
        ]

        root_path = Path(root)
        for filename in filenames:
            file_path = root_path / filename
            if Path(filename).suffix in extensions and not gitignore_spec.match_file(
                str(file_path)
            ):
                files.append(file_path)
    return files


def update_copyright(
    file_path: Path,
    package_config: dict,
    check_only: bool = False,
) -> bool:
    """Update copyright header in file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Get existing copyright years if any
        start_year, _ = get_copyright_years(content)

        # Generate new header
        header_lines = get_copyright_header(
            package_config["header_type"],
            file_path.suffix,
            start_year,
        )

        if check_only:
            # Check if header is up to date
            current_header = "\n".join(header_lines)
            return current_header in content

        # Remove existing copyright header
        content = re.sub(
            r"^(?:/\*|<!--)?\s*(?:#|//|\*)*.*?Copyright.*?(?:\*/|-->)?\s*\n+",
            "",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

        # Add new header
        new_content = "\n".join(header_lines) + "\n" + content.lstrip()

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False


class CopyrightReport:
    """Generate reports about copyright status."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.issues = {
            "missing_headers": [],
            "outdated_years": [],
            "wrong_license": [],
            "style_violations": [],
        }
        self.stats = {
            "total_files": 0,
            "files_with_issues": 0,
            "files_by_package": {},
            "files_by_license": {},
            "files_by_type": {},
        }

    def add_issue(self, issue_type: str, file_path: str, details: str) -> None:
        """Record a copyright issue."""
        self.issues[issue_type].append(
            {
                "file": str(file_path),
                "details": details,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    def add_file_stat(self, file_path: Path, package: str, license_type: str) -> None:
        """Record file statistics."""
        self.stats["total_files"] += 1

        # Group by package
        self.stats["files_by_package"].setdefault(package, 0)
        self.stats["files_by_package"][package] += 1

        # Group by license
        self.stats["files_by_license"].setdefault(license_type, 0)
        self.stats["files_by_license"][license_type] += 1

        # Group by file type
        file_type = file_path.suffix
        self.stats["files_by_type"].setdefault(file_type, 0)
        self.stats["files_by_type"][file_type] += 1

    def generate_json_report(self) -> str:
        """Generate JSON format report."""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "issues": self.issues,
            "statistics": self.stats,
            "summary": {
                "total_issues": sum(len(issues) for issues in self.issues.values()),
                "issue_types": {k: len(v) for k, v in self.issues.items()},
            },
        }
        return json.dumps(report, indent=2)

    def generate_markdown_report(self) -> str:
        """Generate Markdown format report."""
        lines = [
            "# Copyright Status Report",
            f"\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Summary",
            f"- Total files scanned: {self.stats['total_files']}",
            f"- Files with issues: {self.stats['files_with_issues']}",
            "\n## Issues by Type",
        ]

        # Add issue details
        for issue_type, issues in self.issues.items():
            if issues:
                lines.extend(
                    [
                        f"\n### {issue_type.replace('_', ' ').title()}",
                        f"Total: {len(issues)}",
                        "\n| File | Details |",
                        "|------|---------|",
                    ]
                )
                for issue in issues:
                    lines.append(f"| {issue['file']} | {issue['details']} |")

        # Add statistics
        if self.config["grouping"]["by_package"]:
            lines.extend(
                [
                    "\n## Files by Package",
                    "\n| Package | Count |",
                    "|---------|--------|",
                ]
            )
            for package, count in self.stats["files_by_package"].items():
                lines.append(f"| {package} | {count} |")

        return "\n".join(lines)

    def save_reports(self) -> None:
        """Save reports in configured formats."""
        report_dir = Path(self.config["report_dir"])
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        if "json" in self.config["output_formats"]:
            json_path = report_dir / f"copyright_report_{timestamp}.json"
            json_path.write_text(self.generate_json_report())

        if "markdown" in self.config["output_formats"]:
            md_path = report_dir / f"copyright_report_{timestamp}.md"
            md_path.write_text(self.generate_markdown_report())


def main() -> None:
    """Update copyright headers in all source files."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    all_valid = True

    # Initialize report if requested
    report = CopyrightReport(REPORT_CONFIG) if args.report else None

    for package_name, config in PACKAGE_CONFIGS.items():
        if package_name == "root":
            package_dir = root
        else:
            package_dir = root / "packages" / package_name

        if not package_dir.exists():
            continue

        files = find_files(
            package_dir,
            config["extensions"],
            config["exclude_dirs"],
        )

        for file_path in files:
            if report:
                report.add_file_stat(file_path, package_name, config["header_type"])

            if args.check:
                result = update_copyright(file_path, config, check_only=True)
                if not result and report:
                    report.add_issue(
                        "missing_headers",
                        file_path,
                        "Missing or invalid copyright header",
                    )
                all_valid = all_valid and result
            else:
                update_copyright(file_path, config)

    if report:
        report.save_reports()

    if args.check and not all_valid:
        exit(1)


if __name__ == "__main__":
    main()
