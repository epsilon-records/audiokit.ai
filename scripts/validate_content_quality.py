#!/usr/bin/env python3
"""
Content Quality Validator

This script performs advanced validation of context files:
1. Checks for proper markdown structure
2. Validates section headers
3. Ensures proper content organization
4. Checks for required metadata
"""

import os
import sys
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("content_validation.log"), logging.StreamHandler()],
)

# Content validation rules
VALIDATION_RULES = {
    "WHOAMI.md": {
        "required_sections": ["Current Configuration", "Current State", "Capabilities"],
        "required_metadata": ["Model", "Version", "Last Updated"],
        "date_fields": ["Last Updated"],
    },
    "THOUGHTS.md": {
        "required_sections": [
            "Current Mental State",
            "Recent Progress",
            "Current Considerations",
        ],
        "required_metadata": ["Focused on", "Priority", "Status"],
        "date_fields": ["Last Updated"],
    },
    "REFLECTIONS.md": {
        "required_sections": ["Architectural Decisions", "Design Philosophy"],
        "required_metadata": ["Date", "Context", "Decision"],
        "date_fields": ["Date"],
    },
    "TODO.md": {
        "required_sections": ["High Priority", "Medium Priority"],
        "task_format": r"- \[ \].*",  # Tasks should be in checkbox format
        "min_tasks": 1,
    },
    "MAINTENANCE.md": {
        "required_sections": ["Recent Updates", "Upcoming Tasks"],
        "date_format": r"\d{4}-\d{2}-\d{2}",
        "entry_format": r"- \d{4}-\d{2}-\d{2}:.*",
    },
}


def validate_section_exists(content, section):
    """Check if a section exists in the content."""
    return f"## {section}" in content or f"# {section}" in content


def validate_metadata_exists(content, metadata):
    """Check if metadata field exists in the content."""
    return f"- {metadata}:" in content


def validate_date_format(date_str):
    """Validate date string format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_file_content(filename, content):
    """Validate content quality of a specific file."""
    errors = []
    rules = VALIDATION_RULES.get(filename)

    if not rules:
        return []  # No specific rules for this file

    # Check required sections
    for section in rules.get("required_sections", []):
        if not validate_section_exists(content, section):
            errors.append(f"Missing required section: {section}")

    # Check required metadata
    for metadata in rules.get("required_metadata", []):
        if not validate_metadata_exists(content, metadata):
            errors.append(f"Missing required metadata: {metadata}")

    # Check date fields
    for date_field in rules.get("date_fields", []):
        date_pattern = rf"{date_field}: (\d{{4}}-\d{{2}}-\d{{2}})"
        match = re.search(date_pattern, content)
        if match:
            date_str = match.group(1)
            if not validate_date_format(date_str):
                errors.append(f"Invalid date format for {date_field}: {date_str}")
        else:
            errors.append(f"Missing date field: {date_field}")

    # Special handling for TODO.md
    if filename == "TODO.md":
        tasks = re.findall(rules["task_format"], content)
        if len(tasks) < rules["min_tasks"]:
            errors.append(f"TODO.md should have at least {rules['min_tasks']} task(s)")

    return errors


def validate_content_quality():
    """Validate content quality of all context files."""
    context_dir = os.path.join(os.getcwd(), "context")
    if not os.path.isdir(context_dir):
        logging.error("Context directory not found!")
        return False

    all_valid = True
    for filename, rules in VALIDATION_RULES.items():
        filepath = os.path.join(context_dir, filename)
        if not os.path.isfile(filepath):
            logging.error(f"Missing file: {filename}")
            all_valid = False
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            errors = validate_file_content(filename, content)
            if errors:
                logging.error(f"\nValidation errors in {filename}:")
                for error in errors:
                    logging.error(f"  - {error}")
                all_valid = False
            else:
                logging.info(f"✓ {filename} passed quality validation")

        except Exception as e:
            logging.error(f"Error validating {filename}: {str(e)}")
            all_valid = False

    return all_valid


def main():
    try:
        if validate_content_quality():
            logging.info("\nAll files passed content quality validation!")
            sys.exit(0)
        else:
            logging.error("\nContent quality validation failed!")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
