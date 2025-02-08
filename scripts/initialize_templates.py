#!/usr/bin/env python3
"""
Template Initialization Script

Creates initial templates for all context files with proper versioning.
"""

import sys
from datetime import datetime, timedelta
from template_manager import TemplateManager

INITIAL_TEMPLATES = {
    "WHOAMI.md": """# WHOAMI

## Current Configuration
- Model: {model_name}
- Version: {version}
- Last Updated: {date}

## Current State
- Active Project: {project_name}
- Primary Focus: {focus}
- Status: {status}

## Capabilities
- {capability1}
- {capability2}
- {capability3}
""",
    "THOUGHTS.md": """# THOUGHTS

## Current Mental State
- Focused on: {focus}
- Priority: {priority}
- Status: {status}
- Last Updated: {date}

## Recent Progress
- {progress1}
- {progress2}
- {progress3}

## Current Considerations
{considerations}
""",
    "REFLECTIONS.md": """# REFLECTIONS

## Architectural Decisions
- Date: {date}
- Context: {context}
- Decision: {decision}

## Design Philosophy
- {philosophy1}
- {philosophy2}
- {philosophy3}

## Impact Analysis
{impact}
""",
    "TODO.md": """# TODO List

## High Priority
- [ ] {high_priority1}
- [ ] {high_priority2}
- [ ] {high_priority3}

## Medium Priority
- [ ] {medium_priority1}
- [ ] {medium_priority2}

## Low Priority
- [ ] {low_priority1}
""",
    "ROADMAP.md": """# Project Roadmap

## Current Quarter ({quarter})
- {current1}
- {current2}
- {current3}

## Next Quarter
- {next1}
- {next2}
- {next3}

## Long-term Goals
- {goal1}
- {goal2}
- {goal3}
""",
    "RULES.md": """# Development Rules

## Context File Management
- {rule1}
- {rule2}
- {rule3}

## Code Standards
- {standard1}
- {standard2}
- {standard3}

## Workflow Guidelines
- {workflow1}
- {workflow2}
- {workflow3}
""",
    "PROMPT.md": """# Development Priorities

## Current Focus
- {focus1}
- {focus2}
- {focus3}

## Guidelines
- {guideline1}
- {guideline2}
- {guideline3}
""",
    "MAINTENANCE.md": """# Maintenance Log

## Recent Updates
- {date}: {update1}
- {date}: {update2}
- {date}: {update3}

## Upcoming Tasks
- {task1}
- {task2}
- {task3}

## Technical Debt
- {debt1}
- {debt2}
- {debt3}
""",
    "CHANGELOG.txt": """CHANGELOG

{date} - Version {version}
- {change1}
- {change2}
- {change3}

{prev_date} - Version {prev_version}
- {prev_change1}
- {prev_change2}
- {prev_change3}
""",
}


def create_example_values():
    """Create example values for template placeholders."""
    return {
        "model_name": "AudioKit AI Assistant",
        "version": "1.0.0",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "project_name": "AudioKit",
        "focus": "System Development",
        "status": "Active",
        "capability1": "Audio processing and analysis",
        "capability2": "Code generation and review",
        "capability3": "Documentation management",
        "priority": "High",
        "progress1": "Implemented core functionality",
        "progress2": "Added validation system",
        "progress3": "Integrated CI/CD pipeline",
        "considerations": "Focusing on system stability and scalability",
        "context": "Initial system setup",
        "decision": "Implement robust validation",
        "philosophy1": "Maintainability first",
        "philosophy2": "Automated testing",
        "philosophy3": "Clear documentation",
        "impact": "Improved system reliability and maintainability",
        "high_priority1": "Complete validation system",
        "high_priority2": "Implement automated tests",
        "high_priority3": "Set up monitoring",
        "medium_priority1": "Optimize performance",
        "medium_priority2": "Update documentation",
        "low_priority1": "Add additional features",
        "quarter": "Q1 2024",
        "current1": "Implement core features",
        "current2": "Set up infrastructure",
        "current3": "Deploy initial version",
        "next1": "Scale system",
        "next2": "Add advanced features",
        "next3": "Optimize performance",
        "goal1": "Full automation",
        "goal2": "99.9% uptime",
        "goal3": "Global deployment",
        "rule1": "All changes must be validated",
        "rule2": "Documentation required",
        "rule3": "Tests mandatory",
        "standard1": "Follow PEP8",
        "standard2": "Use ESLint",
        "standard3": "Document all functions",
        "workflow1": "Create branch",
        "workflow2": "Write tests",
        "workflow3": "Submit PR",
        "focus1": "Core functionality",
        "focus2": "System stability",
        "focus3": "Documentation",
        "guideline1": "Write clear code",
        "guideline2": "Test thoroughly",
        "guideline3": "Document changes",
        "update1": "Added validation",
        "update2": "Improved testing",
        "update3": "Updated docs",
        "task1": "Implement monitoring",
        "task2": "Add metrics",
        "task3": "Set up alerts",
        "debt1": "Refactor validation",
        "debt2": "Update dependencies",
        "debt3": "Improve error handling",
        "change1": "Initial release",
        "change2": "Added core features",
        "change3": "Set up CI/CD",
        "prev_date": (datetime.now().replace(day=1) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        ),
        "prev_version": "0.9.0",
        "prev_change1": "Beta testing",
        "prev_change2": "Infrastructure setup",
        "prev_change3": "Initial development",
    }


def initialize_templates():
    """Initialize all templates with example content."""
    manager = TemplateManager()
    values = create_example_values()

    for name, template in INITIAL_TEMPLATES.items():
        try:
            content = template.format(**values)
            manager.add_template(name, content, "1.0.0")
            print(f"✓ Created template for {name}")
        except Exception as e:
            print(f"Error creating template for {name}: {str(e)}")
            continue


def main():
    try:
        print("Initializing templates...")
        initialize_templates()
        print("\nTemplate initialization complete!")
    except Exception as e:
        print(f"Error during template initialization: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
