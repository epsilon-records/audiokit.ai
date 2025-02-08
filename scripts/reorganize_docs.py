#!/usr/bin/env python3
"""
Documentation Reorganization Script

This script:
1. Creates the new documentation structure
2. Moves existing files to their new locations
3. Creates placeholder files for missing documentation
4. Updates internal links
"""

import os
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("docs_reorganize.log"), logging.StreamHandler()],
)

# Documentation structure
DOC_STRUCTURE = {
    "getting-started": {
        "QUICKSTART.md": "Quick start guide for AudioKit",
        "INSTALLATION.md": "Installation instructions",
        "FIRST_STEPS.md": "First steps with AudioKit",
    },
    "user-guide": {
        "OVERVIEW.md": "Overview of AudioKit features",
        "AUDIO_PROCESSING.md": "Audio processing capabilities",
        "AI_FEATURES.md": "AI and machine learning features",
        "DAW_INTEGRATION.md": "DAW integration guide",
    },
    "technical": {
        "ARCHITECTURE.md": "System architecture documentation",
        "AUDIO_PROCESSING_GUIDE.md": "Comprehensive audio processing guide",
        "SDK.md": "SDK documentation",
        "API.md": "API reference",
        "FEATURES.md": "Detailed feature specifications",
    },
    "deployment": {
        "OVERVIEW.md": "Deployment overview",
        "GKE.md": "Google Kubernetes Engine setup",
        "TERRAFORM.md": "Terraform configuration",
        "CICD.md": "CI/CD pipeline documentation",
        "PACKAGING.md": "Package and release process",
    },
    "development": {
        "DOCUMENTATION.md": "Documentation guidelines",
        "CODE_STYLE.md": "Code style guidelines",
        "TESTING.md": "Testing procedures",
        "CONTRIBUTING.md": "Contributing guidelines",
    },
}

# File mappings from old to new structure
FILE_MAPPINGS = {
    "SDK.md": "technical/SDK.md",
    "FEATURES.md": "technical/FEATURES.md",
    "GKE.md": "deployment/GKE.md",
    "TERRAFORM.md": "deployment/TERRAFORM.md",
    "PACKAGING.md": "deployment/PACKAGING.md",
    "CICD.md": "deployment/CICD.md",
    "DEPLOYMENT.md": "deployment/OVERVIEW.md",
    "DAW_PROTOCOL.md": "user-guide/DAW_INTEGRATION.md",
    "TECHNICAL.md": "technical/ARCHITECTURE.md",
    "BOOTSTRAP.md": "getting-started/QUICKSTART.md",
    "audio-processing-guide.md": "technical/AUDIO_PROCESSING_GUIDE.md",
    "documentation.md": "development/DOCUMENTATION.md",
    "code-style.md": "development/CODE_STYLE.md",
    "testing.md": "development/TESTING.md",
}


def create_directory_structure(docs_dir):
    """Create the new documentation directory structure."""
    for directory in DOC_STRUCTURE.keys():
        os.makedirs(os.path.join(docs_dir, directory), exist_ok=True)
    logging.info("Created directory structure")


def move_existing_files(docs_dir):
    """Move existing files to their new locations."""
    for old_file, new_path in FILE_MAPPINGS.items():
        old_path = os.path.join(docs_dir, old_file)
        new_full_path = os.path.join(docs_dir, new_path)

        if os.path.exists(old_path):
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
            shutil.move(old_path, new_full_path)
            logging.info(f"Moved {old_file} to {new_path}")
        else:
            logging.warning(f"Source file not found: {old_file}")


def create_placeholder_files(docs_dir):
    """Create placeholder files for missing documentation."""
    for directory, files in DOC_STRUCTURE.items():
        dir_path = os.path.join(docs_dir, directory)
        for filename, description in files.items():
            file_path = os.path.join(dir_path, filename)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write(f"""# {filename.replace('.md', '').title()}

{description}

!!! note "Documentation Needed"
    This page is a placeholder. Content needs to be added.

## Overview

[Add content here]

## Sections to Include

- Section 1
- Section 2
- Section 3

## Related Documentation

- [Link to related doc 1]
- [Link to related doc 2]
""")
                logging.info(f"Created placeholder: {filename}")


def create_index_file(docs_dir):
    """Create main index.md file."""
    index_content = """# AudioKit Documentation

Welcome to the AudioKit documentation. This guide will help you get started with AudioKit's audio processing and AI capabilities.

## Quick Links

- [Quick Start Guide](getting-started/QUICKSTART.md)
- [User Guide](user-guide/OVERVIEW.md)
- [API Reference](technical/API.md)
- [Contributing](development/CONTRIBUTING.md)

## Features

AudioKit provides powerful tools for:

- Audio Processing
- AI-powered Analysis
- DAW Integration
- Cloud Deployment

## Getting Help

- [GitHub Issues](https://github.com/yourusername/audiokit/issues)
- [Documentation](development/DOCUMENTATION.md)
- [Community Support](https://discord.gg/audiokit)

## License

AudioKit is available under the MIT license. See the LICENSE file for more info.
"""

    with open(os.path.join(docs_dir, "index.md"), "w") as f:
        f.write(index_content)
    logging.info("Created index.md")


def update_internal_links(docs_dir):
    """Update internal links in documentation files."""

    def update_links_in_file(filepath):
        with open(filepath, "r") as f:
            content = f.read()

        # Update old style links to new structure
        for old_file, new_path in FILE_MAPPINGS.items():
            content = content.replace(f"]({old_file})", f"]({new_path})")
            content = content.replace(f"](/{old_file})", f"](/{new_path})")

        with open(filepath, "w") as f:
            f.write(content)

    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                update_links_in_file(os.path.join(root, file))
    logging.info("Updated internal links")


def main():
    try:
        docs_dir = os.path.join(os.getcwd(), "docs")

        # Create backup
        backup_dir = os.path.join(os.getcwd(), "docs_backup")
        if os.path.exists(docs_dir):
            shutil.copytree(docs_dir, backup_dir)
            logging.info(f"Created backup at {backup_dir}")

        # Create new structure
        create_directory_structure(docs_dir)

        # Move existing files
        move_existing_files(docs_dir)

        # Create missing files
        create_placeholder_files(docs_dir)

        # Create index
        create_index_file(docs_dir)

        # Update links
        update_internal_links(docs_dir)

        logging.info("Documentation reorganization complete!")
        print("\nDocumentation has been reorganized. Please:")
        print("1. Review the changes")
        print("2. Update mkdocs.yml if needed")
        print("3. Build the documentation to verify")
        print(f"4. Delete the backup at {backup_dir} if satisfied")

    except Exception as e:
        logging.error(f"Reorganization failed: {str(e)}")
        if os.path.exists(backup_dir):
            shutil.rmtree(docs_dir)
            shutil.move(backup_dir, docs_dir)
            logging.info("Restored from backup")
        sys.exit(1)


if __name__ == "__main__":
    main()
