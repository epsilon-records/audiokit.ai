#!/usr/bin/env python3
"""
Template Manager for Context Files

This script manages versioned templates for context files:
1. Stores templates with version history
2. Updates templates while maintaining backward compatibility
3. Provides template migration tools
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
    handlers=[logging.FileHandler("template_manager.log"), logging.StreamHandler()],
)


class TemplateManager:
    def __init__(self):
        self.template_dir = os.path.join(os.getcwd(), "context", ".templates")
        self.version_file = os.path.join(self.template_dir, "versions.json")
        self.ensure_template_directory()

    def ensure_template_directory(self):
        """Create template directory if it doesn't exist."""
        os.makedirs(self.template_dir, exist_ok=True)
        if not os.path.exists(self.version_file):
            self._save_versions({})

    def _load_versions(self):
        """Load template version information."""
        try:
            with open(self.version_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_versions(self, versions):
        """Save template version information."""
        with open(self.version_file, "w") as f:
            json.dump(versions, f, indent=2)

    def add_template(self, name, content, version="1.0.0"):
        """Add a new template or update existing one."""
        versions = self._load_versions()
        template_info = versions.get(name, {"versions": {}})

        # Store the new version
        template_info["versions"][version] = {
            "content": content,
            "created_at": datetime.now().isoformat(),
            "created_by": os.environ.get("USER", "unknown"),
        }

        # Update latest version
        template_info["latest_version"] = version
        versions[name] = template_info

        # Save version info
        self._save_versions(versions)
        logging.info(f"Added template {name} version {version}")

    def get_template(self, name, version=None):
        """Get a specific template version or latest."""
        versions = self._load_versions()
        if name not in versions:
            raise ValueError(f"Template {name} not found")

        template_info = versions[name]
        if version is None:
            version = template_info["latest_version"]

        if version not in template_info["versions"]:
            raise ValueError(f"Version {version} not found for template {name}")

        return template_info["versions"][version]["content"]

    def list_templates(self):
        """List all available templates and their versions."""
        versions = self._load_versions()
        result = []

        for name, info in versions.items():
            template_versions = list(info["versions"].keys())
            result.append(
                {
                    "name": name,
                    "latest_version": info["latest_version"],
                    "versions": template_versions,
                }
            )

        return result

    def migrate_template(self, name, from_version, to_version):
        """Migrate a template from one version to another."""
        old_content = self.get_template(name, from_version)
        new_content = self.get_template(name, to_version)

        # Create backup of old file
        backup_dir = os.path.join(self.template_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"{name}_{from_version}_{timestamp}.bak")

        with open(backup_file, "w") as f:
            f.write(old_content)

        return new_content


def main():
    """CLI interface for template management."""
    manager = TemplateManager()

    if len(sys.argv) < 2:
        print("Usage: template_manager.py [list|add|get|migrate] [args...]")
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "list":
            templates = manager.list_templates()
            print("\nAvailable Templates:")
            for template in templates:
                print(f"\n{template['name']}:")
                print(f"  Latest Version: {template['latest_version']}")
                print("  All Versions:", ", ".join(template["versions"]))

        elif command == "add" and len(sys.argv) >= 4:
            name = sys.argv[2]
            version = sys.argv[3]
            print("Enter template content (Ctrl+D to finish):")
            content = sys.stdin.read()
            manager.add_template(name, content, version)
            print(f"Added template {name} version {version}")

        elif command == "get" and len(sys.argv) >= 3:
            name = sys.argv[2]
            version = sys.argv[3] if len(sys.argv) > 3 else None
            content = manager.get_template(name, version)
            print(f"\nTemplate {name} (version {version or 'latest'}):")
            print(content)

        elif command == "migrate" and len(sys.argv) >= 5:
            name = sys.argv[2]
            from_version = sys.argv[3]
            to_version = sys.argv[4]
            content = manager.migrate_template(name, from_version, to_version)
            print(f"Migrated {name} from {from_version} to {to_version}")
            print("New content:")
            print(content)

        else:
            print("Invalid command or missing arguments")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
