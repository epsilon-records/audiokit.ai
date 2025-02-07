#!/usr/bin/env python3
"""
Validation Script for Context Files

This script ensures that all required context files exist in the 'context/' directory
and that they contain at least minimal content.
"""

import os
import sys

def validate_context_files():
    # List of required context files
    required_files = [
        "WHOAMI.md",
        "THOUGHTS.md",
        "REFLECTIONS.md",
        "TODO.md",
        "ROADMAP.md",
        "RULES.md",
        "PROMPT.md",
        "MAINTENANCE.md",
        "CHANGELOG.txt",
    ]
    
    context_dir = os.path.join(os.getcwd(), "context")
    errors = []

    if not os.path.isdir(context_dir):
        errors.append("Context directory 'context/' does not exist!")
    else:
        for filename in required_files:
            filepath = os.path.join(context_dir, filename)
            if not os.path.isfile(filepath):
                errors.append(f"Missing required context file: {filename}")
            else:
                # Basic sanity check for markdown files (at least 10 characters)
                if filename.endswith(".md"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if len(content) < 10:
                            errors.append(f"File {filename} appears to be empty or too short.")
    
    if errors:
        print("Validation FAILED:")
        for error in errors:
            print(" -", error)
        sys.exit(1)
    else:
        print("Validation SUCCESS: All context files are in place and appear valid.")

if __name__ == "__main__":
    validate_context_files() 