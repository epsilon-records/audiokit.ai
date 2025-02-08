#!/usr/bin/env python3
"""
Documentation Generator using LLM

Uses OpenAI's API to regenerate documentation files in both root and package directories
based on the current state of the codebase.
"""

import os
import sys
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Documentation validation rules
DOC_RULES = {
    "README.md": {
        "required_sections": [
            "Installation",
            "Usage",
            "Documentation",
            "Contributing",
            "License",
        ],
        "min_length": 1000,
        "needs_code_examples": True,
    },
    "DEVELOPER.md": {
        "required_sections": ["Setup", "Development", "Testing", "Deployment"],
        "min_length": 800,
        "needs_code_examples": True,
    },
    "CHANGELOG.md": {
        "required_sections": ["Unreleased", "Released"],
        "min_length": 200,
        "date_format": r"\d{4}-\d{2}-\d{2}",
    },
    "CONTRIBUTING.md": {
        "required_sections": ["Code Style", "Pull Requests", "Testing"],
        "min_length": 500,
        "needs_code_examples": True,
    },
}


def validate_doc_content(content, doc_type):
    """Validate documentation content against rules."""
    rules = DOC_RULES.get(doc_type, {})
    issues = []

    # Check minimum length
    if rules.get("min_length") and len(content) < rules["min_length"]:
        issues.append(
            f"Content length below minimum ({len(content)}/{rules['min_length']})"
        )

    # Check required sections
    for section in rules.get("required_sections", []):
        if not re.search(rf"#{{1,6}}\s+{section}", content, re.IGNORECASE):
            issues.append(f"Missing required section: {section}")

    # Check for code examples
    if rules.get("needs_code_examples") and not re.search(r"```[a-z]*\n", content):
        issues.append("Missing code examples")

    # Check date format
    if rules.get("date_format"):
        if not re.search(rules["date_format"], content):
            issues.append(
                f"Missing or invalid date format (required: {rules['date_format']})"
            )

    return issues


def get_project_structure(root_dir="."):
    """Get a summary of the project structure."""
    structure = []
    for root, dirs, files in os.walk(root_dir):
        if any(p in root for p in [".git", "__pycache__", "node_modules", "site"]):
            continue
        level = root.replace(root_dir, "").count(os.sep)
        indent = "  " * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        for file in sorted(files):
            if not file.startswith("."):
                structure.append(f"{indent}  {file}")
    return "\n".join(structure)


def get_file_content(path):
    """Safely read file content."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return ""


def generate_root_readme(client):
    """Generate root README.md content."""
    structure = get_project_structure()
    mkdocs = get_file_content("mkdocs.yml")
    setup = get_file_content("setup.py") or get_file_content("pyproject.toml")
    existing = get_file_content("README.md")

    prompt = f"""Generate a comprehensive README.md for the root of an audio processing and AI toolkit.
    
    Project Structure:
    {structure}
    
    Documentation Structure (mkdocs.yml):
    {mkdocs}
    
    Setup Information:
    {setup}
    
    Existing README:
    {existing}
    
    Requirements:
    1. Start with a brief, compelling introduction
    2. Include badges for build status, version, license
    3. Add clear installation instructions
    4. Provide quick start examples
    5. Link to full documentation
    6. Include contribution guidelines
    7. Add license information
    8. Use modern markdown features
    9. Preserve any custom sections from existing README
    10. Ensure links to documentation site are correct
    11. Reference the AudioKit AI package
    
    Format the README in clean, modern markdown with proper sections and formatting."""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a technical documentation expert. Preserve existing content where appropriate and enhance it.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def generate_audiokit_readme(client, package_path):
    """Generate README.md for the core AudioKit package."""
    pkg_structure = get_project_structure(package_path)
    pkg_setup = get_file_content(
        os.path.join(package_path, "setup.py")
    ) or get_file_content(os.path.join(package_path, "pyproject.toml"))
    existing_readme = get_file_content(os.path.join(package_path, "README.md"))

    readme_prompt = f"""Generate a comprehensive README.md for the core AudioKit package.
    
    Package Structure:
    {pkg_structure}
    
    Setup Information:
    {pkg_setup}
    
    Existing README:
    {existing_readme}
    
    Requirements:
    1. Focus on core audio processing features
    2. Include package-specific installation instructions
    3. Provide audio processing examples
    4. Link to main project documentation
    5. List audio processing dependencies
    6. Include performance recommendations
    7. Add audio format compatibility information
    8. Preserve any custom sections
    
    Format the README in clean, modern markdown with proper sections and formatting."""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a technical documentation expert focusing on audio processing systems.",
            },
            {"role": "user", "content": readme_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def generate_package_docs(client, package_path):
    """Generate README.md and DEVELOPER.md for a package."""
    pkg_structure = get_project_structure(package_path)
    pkg_setup = get_file_content(
        os.path.join(package_path, "setup.py")
    ) or get_file_content(os.path.join(package_path, "pyproject.toml"))
    existing_readme = get_file_content(os.path.join(package_path, "README.md"))
    existing_dev = get_file_content(os.path.join(package_path, "DEVELOPER.md"))

    # Generate package README
    readme_prompt = f"""Generate a comprehensive README.md for the AudioKit AI package.
    
    Package Structure:
    {pkg_structure}
    
    Setup Information:
    {pkg_setup}
    
    Existing README:
    {existing_readme}
    
    Requirements:
    1. Focus on AI-specific features and capabilities
    2. Include package-specific installation instructions
    3. Provide AI model usage examples
    4. Link to main project documentation
    5. List AI-specific dependencies
    6. Include model compatibility information
    7. Add performance recommendations
    8. Preserve any custom sections
    
    Format the README in clean, modern markdown with proper sections and formatting."""

    readme_response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a technical documentation expert focusing on AI and ML systems.",
            },
            {"role": "user", "content": readme_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    # Generate package DEVELOPER.md
    dev_prompt = f"""Generate a comprehensive DEVELOPER.md for the AudioKit AI package.
    
    Package Structure:
    {pkg_structure}
    
    Existing Guide:
    {existing_dev}
    
    Requirements:
    1. AI model development guidelines
    2. Training pipeline setup
    3. Model evaluation procedures
    4. Data preparation guidelines
    5. Performance optimization tips
    6. Testing AI components
    7. Model deployment process
    8. Preserve any custom sections
    
    Format the guide in clear markdown with proper sections and code examples."""

    dev_response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a technical documentation expert focusing on AI development practices.",
            },
            {"role": "user", "content": dev_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return readme_response.choices[0].message.content, dev_response.choices[
        0
    ].message.content


def generate_changelog(client, package_path):
    """Generate CHANGELOG.md for a package."""
    pkg_structure = get_project_structure(package_path)
    existing = get_file_content(os.path.join(package_path, "CHANGELOG.md"))

    prompt = f"""Generate a CHANGELOG.md for the package.
    
    Package Structure:
    {pkg_structure}
    
    Existing Changelog:
    {existing}
    
    Requirements:
    1. Follow Keep a Changelog format
    2. Include Unreleased section at top
    3. Group changes by type (Added, Changed, Deprecated, Removed, Fixed, Security)
    4. Use ISO date format (YYYY-MM-DD)
    5. Preserve existing version history
    6. Add links to version tags
    
    Format in clean markdown following Keep a Changelog standards."""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a technical documentation expert focusing on change management.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def generate_contributing(client, package_path):
    """Generate CONTRIBUTING.md for a package."""
    pkg_structure = get_project_structure(package_path)
    existing = get_file_content(os.path.join(package_path, "CONTRIBUTING.md"))

    prompt = f"""Generate a CONTRIBUTING.md guide for the package.
    
    Package Structure:
    {pkg_structure}
    
    Existing Guide:
    {existing}
    
    Requirements:
    1. Code style guidelines
    2. Pull request process
    3. Testing requirements
    4. Documentation requirements
    5. Development setup
    6. Include code examples
    7. Review process
    8. Release process
    
    Format in clear markdown with proper sections and examples."""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a technical documentation expert focusing on development processes.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def main():
    # Check for API key in environment after loading .env
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in your environment or .env file")
        sys.exit(1)

    client = OpenAI()

    try:
        # Generate root README.md
        root_readme = generate_root_readme(client)
        with open("README.md", "w") as f:
            f.write(root_readme)
        print("Generated root README.md")

        issues = validate_doc_content(root_readme, "README.md")
        if issues:
            print("\nWarnings for root README.md:")
            for issue in issues:
                print(f"- {issue}")

        # Generate core AudioKit package documentation
        audiokit_path = "packages/audiokit"
        if os.path.exists(audiokit_path):
            # Generate and validate README.md
            audiokit_readme = generate_audiokit_readme(client, audiokit_path)
            readme_path = os.path.join(audiokit_path, "README.md")
            with open(readme_path, "w") as f:
                f.write(audiokit_readme)
            print("Generated AudioKit package README.md")

            issues = validate_doc_content(audiokit_readme, "README.md")
            if issues:
                print("\nWarnings for AudioKit README.md:")
                for issue in issues:
                    print(f"- {issue}")

            # Generate additional documentation
            changelog = generate_changelog(client, audiokit_path)
            with open(os.path.join(audiokit_path, "CHANGELOG.md"), "w") as f:
                f.write(changelog)
            print("Generated AudioKit CHANGELOG.md")

            contributing = generate_contributing(client, audiokit_path)
            with open(os.path.join(audiokit_path, "CONTRIBUTING.md"), "w") as f:
                f.write(contributing)
            print("Generated AudioKit CONTRIBUTING.md")

        # Generate AI package documentation
        ai_path = "packages/audiokit_ai"
        if os.path.exists(ai_path):
            # Generate and validate README.md and DEVELOPER.md
            ai_readme, ai_dev = generate_package_docs(client, ai_path)

            with open(os.path.join(ai_path, "README.md"), "w") as f:
                f.write(ai_readme)
            print("Generated AudioKit AI package README.md")

            with open(os.path.join(ai_path, "DEVELOPER.md"), "w") as f:
                f.write(ai_dev)
            print("Generated AudioKit AI package DEVELOPER.md")

            issues = validate_doc_content(ai_readme, "README.md")
            if issues:
                print("\nWarnings for AudioKit AI README.md:")
                for issue in issues:
                    print(f"- {issue}")

            issues = validate_doc_content(ai_dev, "DEVELOPER.md")
            if issues:
                print("\nWarnings for AudioKit AI DEVELOPER.md:")
                for issue in issues:
                    print(f"- {issue}")

            # Generate additional documentation
            changelog = generate_changelog(client, ai_path)
            with open(os.path.join(ai_path, "CHANGELOG.md"), "w") as f:
                f.write(changelog)
            print("Generated AudioKit AI CHANGELOG.md")

            contributing = generate_contributing(client, ai_path)
            with open(os.path.join(ai_path, "CONTRIBUTING.md"), "w") as f:
                f.write(contributing)
            print("Generated AudioKit AI CONTRIBUTING.md")

    except Exception as e:
        print(f"Error generating documentation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
