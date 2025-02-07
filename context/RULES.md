# RULES

## Coding Standards
- Adhere to established style guidelines for Python, JavaScript, and Markdown.
- Use Ruff for Python PEP8 compliance and ESLint for JavaScript consistency.

## Documentation Standards
- Store all context files in the `context/` directory located at the project root.
- Update WHOAMI.md on every execution.
- Log technical insights in THOUGHTS.md.
- Document architectural decisions in REFLECTIONS.md.
- Track tasks in TODO.md.
- Outline release schedules and project initiatives in ROADMAP.md.
- Maintain an up-to-date changelog in CHANGELOG.txt.

## Development Workflow
- Code reviews are mandatory before merging changes.
- Regular audits must be performed to ensure compliance with these rules.
- Automated validation of context files using CI/CD tools (see validate_context_files.yml) is required.

## Exceptions
- In emergency situations, bypasses to standard code reviews must be documented and reviewed retroactively. 