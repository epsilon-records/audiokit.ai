#!/usr/bin/env python3
"""
Documentation Link Checker

This script:
1. Scans all markdown files for links
2. Validates internal links point to existing files
3. Checks for broken section references
4. Reports any broken links
"""

import os
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("link_check.log"), logging.StreamHandler()],
)


def find_markdown_files(docs_dir):
    """Find all markdown files in the documentation directory."""
    return list(Path(docs_dir).rglob("*.md"))


def extract_links(content):
    """Extract all markdown links from content."""
    # Match [text](link) pattern
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    return re.findall(link_pattern, content)


def validate_internal_link(link, file_path, docs_dir):
    """Validate an internal documentation link."""
    if link.startswith(("http://", "https://", "mailto:")):
        return True  # Skip external links

    # Handle section references
    if "#" in link:
        file_part, section = link.split("#", 1)
        if not file_part:
            return True  # Same-file section reference
    else:
        file_part = link
        section = None

    # Resolve relative path
    if not file_part:
        target_path = file_path
    elif file_part.startswith("/"):
        target_path = Path(docs_dir) / file_part.lstrip("/")
    else:
        target_path = file_path.parent / file_part

    # Normalize path
    try:
        target_path = target_path.resolve()
        if not target_path.exists():
            return False
    except Exception:
        return False

    # Check section reference if present
    if section:
        try:
            content = target_path.read_text()
            section_pattern = f"#{{1,6}} {section.replace('-', ' ')}"
            if not re.search(section_pattern, content, re.IGNORECASE):
                return False
        except Exception:
            return False

    return True


def check_links(docs_dir):
    """Check all links in documentation files."""
    broken_links = []
    files = find_markdown_files(docs_dir)

    for file_path in files:
        try:
            content = file_path.read_text()
            links = extract_links(content)

            for text, link in links:
                if not validate_internal_link(link, file_path, docs_dir):
                    broken_links.append(
                        {
                            "file": str(file_path.relative_to(docs_dir)),
                            "text": text,
                            "link": link,
                        }
                    )
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            continue

    return broken_links


def main():
    docs_dir = os.path.join(os.getcwd(), "docs")

    logging.info("Checking documentation links...")
    broken_links = check_links(docs_dir)

    if broken_links:
        logging.error("\nBroken links found:")
        for link in broken_links:
            logging.error(f"In {link['file']}: [{link['text']}]({link['link']})")
        return 1
    else:
        logging.info("\nAll documentation links are valid!")
        return 0


if __name__ == "__main__":
    exit(main())
