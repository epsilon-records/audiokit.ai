#!/usr/bin/env python3
"""
Validation Script for Context Files

This script ensures that all required context files exist in the 'context/' directory
and that they contain at least minimal content. It provides detailed reporting and
handles validation failures according to project rules.
"""

import os
import sys
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("context_validation.log"), logging.StreamHandler()],
)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def check_emergency_bypass():
    """Check if there's an emergency bypass flag set."""
    bypass_file = os.path.join(os.getcwd(), "context", ".emergency_bypass")
    if os.path.exists(bypass_file):
        try:
            with open(bypass_file, "r") as f:
                bypass_data = json.load(f)
                if bypass_data.get("active", False):
                    expiry = datetime.fromisoformat(bypass_data.get("expiry", ""))
                    if expiry > datetime.now():
                        logging.warning("Emergency bypass active until %s", expiry)
                        return True
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
    return False


def generate_validation_report(errors):
    """Generate a detailed validation report with recommendations."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "FAILED" if errors else "SUCCESS",
        "errors": errors,
        "recommendations": [],
    }

    for error in errors:
        if "Missing required context file" in error:
            filename = error.split(": ")[1]
            report["recommendations"].append(
                f"Create {filename} in the context/ directory"
            )
        elif "empty or too short" in error:
            filename = error.split(" ")[1]
            report["recommendations"].append(
                f"Add proper content to {filename} following documentation standards"
            )

    return report


def validate_context_files():
    # List of required context files with minimum content requirements
    required_files = [
        ("WHOAMI.md", 100),  # Minimum 100 chars for identity info
        ("THOUGHTS.md", 50),  # Minimum 50 chars for thoughts
        ("REFLECTIONS.md", 100),  # Minimum 100 chars for architectural decisions
        ("TODO.md", 30),  # Minimum 30 chars for task list
        ("ROADMAP.md", 100),  # Minimum 100 chars for project planning
        ("RULES.md", 100),  # Minimum 100 chars for rules
        ("PROMPT.md", 50),  # Minimum 50 chars for prompts
        ("MAINTENANCE.md", 50),  # Minimum 50 chars for maintenance notes
        ("CHANGELOG.txt", 30),  # Minimum 30 chars for changelog
    ]
    
    context_dir = os.path.join(os.getcwd(), "context")
    errors = []

    if not os.path.isdir(context_dir):
        errors.append("Context directory 'context/' does not exist!")
    else:
        for filename, min_length in required_files:
            filepath = os.path.join(context_dir, filename)
            if not os.path.isfile(filepath):
                errors.append(f"Missing required context file: {filename}")
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if len(content) < min_length:
                            errors.append(
                                f"File {filename} content too short. "
                                f"Minimum {min_length} characters required."
                            )
                except Exception as e:
                    errors.append(f"Error reading {filename}: {str(e)}")

    # Generate and log validation report
    report = generate_validation_report(errors)
    logging.info("Validation Report:\n%s", json.dumps(report, indent=2))

    # Check for emergency bypass
    if errors and not check_emergency_bypass():
        print("\nValidation FAILED:")
        for error in errors:
            print(" -", error)
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(" -", rec)
        sys.exit(1)
    else:
        if errors:
            print("\nValidation FAILED but proceeding due to emergency bypass")
        else:
            print("\nValidation SUCCESS: All context files are in place and valid.")


# Add validation for new required sections
def validate_section_exists(content, section):
    """Check if a section exists in the content."""
    return f"## {section}" in content or f"# {section}" in content

# Add validation for audio node documentation
VALIDATION_RULES = {
    "THOUGHTS.md": {
        "required_sections": [
            "Current Mental State",
            "Recent Progress", 
            "Current Considerations",
            "AudioNode Architecture"  # New required section
        ],
        # ... existing rules
    }
}

if __name__ == "__main__":
    try:
    validate_context_files() 
    except Exception as e:
        logging.error("Unexpected error during validation: %s", str(e))
        sys.exit(1)
